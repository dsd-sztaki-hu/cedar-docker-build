FROM metadatacenter/cedar-java:2.8.0

ENV CEDAR_HOME=/cedar

ENV CEDAR_VERSION=2.8.0

ENV CEDAR_RESOURCE_HTTP_PORT=9007

ADD scripts/docker-entrypoint.sh ${CEDAR_HOME}/

# script to install jar
ADD include/install_deps.sh ${CEDAR_HOME}/

RUN mkdir -p ${CEDAR_HOME}/app
WORKDIR ${CEDAR_HOME}/app/

ADD scripts/cedarat.sh ${CEDAR_HOME}/app

ENV CADIR=${CEDAR_HOME}/ca/
RUN mkdir -p ${CADIR}
VOLUME ${CADIR}

RUN microdnf update -y
RUN microdnf install -y vim iputils hostname
RUN microdnf clean all

ARG CEDAR_MAVEN_REPO_URL=https://nexus.bmir.stanford.edu
ARG CEDAR_MAVEN_SNAPSHOTS_URL=https://nexus.bmir.stanford.edu/repository/snapshots
ARG CEDAR_MAVEN_RELEASES_URL=https://nexus.bmir.stanford.edu/repository/releases
ARG CEDAR_NEXUS_USERNAME
ARG CEDAR_NEXUS_PASSWORD
ENV CEDAR_MAVEN_REPO_URL=${CEDAR_MAVEN_REPO_URL}
ENV CEDAR_MAVEN_SNAPSHOTS_URL=${CEDAR_MAVEN_SNAPSHOTS_URL}
ENV CEDAR_MAVEN_RELEASES_URL=${CEDAR_MAVEN_RELEASES_URL}
ENV CEDAR_NEXUS_USERNAME=${CEDAR_NEXUS_USERNAME}
ENV CEDAR_NEXUS_PASSWORD=${CEDAR_NEXUS_PASSWORD}

ADD config/m2/settings.xml /root/.m2/

RUN echo 'alias cedarat="/cedar/app/cedarat.sh"' >> ~/.bashrc

RUN ${CEDAR_HOME}/install_deps.sh

CMD ["bash", "-C", "/cedar/docker-entrypoint.sh"]
