#!/bin/bash
set -e

echo "Executing sed"

INDEX_HTML="${CEDAR_FRONTEND_HOME}/cedar-bridging-dist/index.html"
if [ -f "$INDEX_HTML" ]; then
  sed -i 's/window.cedarDomain = \".*\"/window.cedarDomain = \"'${CEDAR_HOST}'\"/g' "$INDEX_HTML"
  sed -i 's/content\.metadatacenter\.org\//content\.'${CEDAR_HOST}'\//g' "$INDEX_HTML"
fi

exec "$@"
