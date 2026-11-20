"""Flip a CEDAR artifact between draft and published without changing its version.

The resource server rejects writes to a published artifact and has no unpublish
command. This service changes bibo:status in MongoDB and Neo4j, and the matching
search field, so the template editor can PUT the body and then publish again at
the same pav:version.
"""

import logging
import os
from urllib.parse import quote, urlparse

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from neo4j import GraphDatabase
from pydantic import BaseModel, ConfigDict, Field
from pymongo import MongoClient

log = logging.getLogger("infra-unpublish")
logging.basicConfig(level=logging.INFO)

DRAFT = "bibo:draft"
PUBLISHED = "bibo:published"

# URL path segment -> Mongo collection. Instances are rejected below.
COLLECTIONS = {
    "templates": "templates",
    "template-elements": "template-elements",
    "template-fields": "template-fields",
}

ADMIN_ROLE = "userAdministrator"


def required_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(name + " is required")
    return value


def resource_base_url():
    explicit = os.environ.get("CEDAR_RESOURCE_BASE_URL")
    if explicit:
        return explicit.rstrip("/")
    return "http://%s:%s" % (
        required_env("CEDAR_RESOURCE_SERVER_HOST"),
        os.environ.get("CEDAR_RESOURCE_HTTP_PORT", "9007"),
    )


def mongo_client():
    return MongoClient(
        host=required_env("CEDAR_MONGO_HOST"),
        port=int(os.environ.get("CEDAR_MONGO_PORT", "27017")),
        username=required_env("CEDAR_MONGO_APP_USER_NAME"),
        password=required_env("CEDAR_MONGO_APP_USER_PASSWORD"),
        authSource=os.environ.get("CEDAR_MONGO_AUTH_SOURCE", os.environ.get("CEDAR_MONGO_DB", "cedar")),
        authMechanism="SCRAM-SHA-1",
    )


def neo4j_driver():
    uri = "bolt://%s:%s" % (
        required_env("CEDAR_NEO4J_HOST"),
        os.environ.get("CEDAR_NEO4J_BOLT_PORT", "7687"),
    )
    return GraphDatabase.driver(
        uri,
        auth=(required_env("CEDAR_NEO4J_USER_NAME"), required_env("CEDAR_NEO4J_USER_PASSWORD")),
    )


MONGO = mongo_client()
NEO4J = neo4j_driver()
DB_NAME = os.environ.get("CEDAR_MONGO_DB", "cedar")
RESOURCE_BASE = resource_base_url()
OPENSEARCH_BASE = "http://%s:%s" % (
    required_env("CEDAR_OPENSEARCH_HOST"),
    os.environ.get("CEDAR_OPENSEARCH_REST_PORT", "9200"),
)
OPENSEARCH_INDEX = os.environ.get("CEDAR_OPENSEARCH_INDEX", "cedar-search")
OPENSEARCH_USER = os.environ.get("CEDAR_OPENSEARCH_USER") or None
OPENSEARCH_PASSWORD = os.environ.get("CEDAR_OPENSEARCH_PASSWORD") or None

app = FastAPI(title="infra-unpublish-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    # Unhandled errors are turned into a normal response so the browser can
    # read them. HTTPException keeps its own handler.
    log.exception("Publication status update failed")
    return JSONResponse(status_code=500, content={"detail": "Publication status update failed"})


class StatusBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    artifact_id: str = Field(alias="@id")
    publication_status: str = Field(alias="publicationStatus")


def api_key_from_header(authorization):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    prefix = "apikey "
    if not authorization.lower().startswith(prefix):
        raise HTTPException(status_code=401, detail="Authorization must be an apiKey")
    key = authorization[len(prefix):].strip()
    if not key:
        raise HTTPException(status_code=401, detail="Missing API key")
    return key


def collection_for(artifact_id):
    path = urlparse(artifact_id).path
    parts = [part for part in path.split("/") if part]
    if not parts:
        raise HTTPException(status_code=400, detail="@id path is missing a resource type")
    kind = parts[0]
    if kind == "template-instances":
        raise HTTPException(status_code=400, detail="Instances cannot change publication status")
    collection = COLLECTIONS.get(kind)
    if collection is None:
        raise HTTPException(status_code=400, detail="Unsupported resource type in @id")
    return kind, collection


def assert_administrator(api_key):
    with NEO4J.session() as session:
        admin = session.run(
            "MATCH (user:User) "
            "WHERE $apiKey IN user.apiKeys AND $role IN user.roles "
            "RETURN user LIMIT 1",
            apiKey=api_key,
            role=ADMIN_ROLE,
        ).single()
        if admin is not None:
            return
        known = session.run(
            "MATCH (user:User) WHERE $apiKey IN user.apiKeys RETURN user LIMIT 1",
            apiKey=api_key,
        ).single()
    if known is None:
        raise HTTPException(status_code=401, detail="Unknown API key")
    raise HTTPException(status_code=403, detail="userAdministrator role is required")


def assert_can_write(api_key, artifact_id, route):
    url = "%s/%s/%s/report" % (RESOURCE_BASE, route, quote(artifact_id, safe=""))
    try:
        response = httpx.get(
            url,
            headers={"Authorization": "apiKey " + api_key, "Accept": "application/json"},
            timeout=30.0,
        )
    except httpx.HTTPError as error:
        log.exception("Resource server report failed")
        raise HTTPException(status_code=502, detail="Resource server could not be reached") from error

    if response.status_code in (401, 403):
        raise HTTPException(status_code=401, detail="API key was rejected by the resource server")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Artifact was not found")
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Resource server returned %s" % response.status_code,
        )

    permissions = (response.json() or {}).get("currentUserPermissions") or {}
    if not permissions.get("canWrite"):
        raise HTTPException(status_code=403, detail="You do not have write access to this artifact")


def mongo_artifact(collection_name, artifact_id):
    collection = MONGO[DB_NAME][collection_name]
    found = collection.find_one({"@id": artifact_id}, {"pav:version": 1})
    if found is None:
        raise HTTPException(status_code=404, detail="Artifact was not found in MongoDB")
    return collection, found.get("pav:version")


def set_mongo_status(collection, artifact_id, status):
    # pav:version is left in place so the same version can be published again.
    collection.update_one({"@id": artifact_id}, {"$set": {"bibo:status": status}})


def set_neo4j_status(artifact_id, status):
    is_draft = status == DRAFT
    with NEO4J.session() as session:
        record = session.run(
            "MATCH (n {_id: $identifier}) "
            "SET n.bibo_status = $status, "
            "    n.isLatestDraftVersion = $isDraft, "
            "    n.isLatestPublishedVersion = $isPublished "
            "RETURN n.pav_version AS version",
            identifier=artifact_id,
            status=status,
            isDraft=is_draft,
            isPublished=not is_draft,
        ).single()
    if record is None:
        raise HTTPException(status_code=404, detail="Artifact was not found in Neo4j")
    return record["version"]


def set_search_status(artifact_id, status):
    """Update the search document. A search failure does not undo the database write."""
    url = "%s/%s/_update_by_query?refresh=true&conflicts=proceed" % (OPENSEARCH_BASE, OPENSEARCH_INDEX)
    body = {
        "query": {"term": {"info.@id": artifact_id}},
        "script": {
            "lang": "painless",
            "source": "if (ctx._source.info == null) { ctx._source.info = new HashMap(); } ctx._source.info['bibo:status'] = params.status;",
            "params": {"status": status},
        },
    }
    auth = None
    if OPENSEARCH_USER:
        auth = (OPENSEARCH_USER, OPENSEARCH_PASSWORD or "")
    try:
        response = httpx.post(url, json=body, auth=auth, timeout=30.0)
    except httpx.HTTPError:
        log.exception("OpenSearch update failed for %s", artifact_id)
        return
    if response.status_code >= 300:
        log.error("OpenSearch update failed: %s %s", response.status_code, response.text)
        return
    updated = (response.json() or {}).get("updated", 0)
    if updated == 0:
        log.warning("OpenSearch has no document for %s", artifact_id)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/status")
def set_status(body: StatusBody, authorization: str = Header(default=None)):
    if body.publication_status not in (DRAFT, PUBLISHED):
        raise HTTPException(status_code=400, detail="publicationStatus must be bibo:draft or bibo:published")

    api_key = api_key_from_header(authorization)
    route, collection = collection_for(body.artifact_id)
    assert_administrator(api_key)
    assert_can_write(api_key, body.artifact_id, route)

    # Confirm the document exists before Neo4j changes. Neo4j is what the
    # resource server checks before it allows a PUT.
    mongo_collection, version = mongo_artifact(collection, body.artifact_id)
    neo4j_version = set_neo4j_status(body.artifact_id, body.publication_status)
    set_mongo_status(mongo_collection, body.artifact_id, body.publication_status)
    if not version:
        version = neo4j_version
    set_search_status(body.artifact_id, body.publication_status)

    return {
        "@id": body.artifact_id,
        "pav:version": version,
        "bibo:status": body.publication_status,
    }
