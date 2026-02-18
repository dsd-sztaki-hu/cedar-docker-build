FROM nginx:1.23.4

ENV CEDAR_VERSION=2.8.0
ENV CEDAR_METADATA_CENTER_REPO=https://github.com/metadatacenter
ENV PACKAGE_NAME=cedar-monitoring
ENV TAGS_PREFIX=archive/refs/tags
ENV TAG=release-${CEDAR_VERSION}

# Add the entry point
ADD scripts/docker-entrypoint.sh /

# Add nginx config
ADD config/*.conf /etc/nginx/conf.d/

# Update and install curl
RUN \
apt-get update && \
apt-get install -y apt-utils && \
apt-get install -y curl

ENV CEDAR_HOME /srv/cedar
ENV CEDAR_FRONTEND_HOME ${CEDAR_HOME}/${PACKAGE_NAME}/

# Create CEDAR application home directory
RUN mkdir -p ${CEDAR_FRONTEND_HOME}
WORKDIR ${CEDAR_FRONTEND_HOME}

ENV TARBALL ${TAG}.tar.gz
ENV PACKAGE_URI ${CEDAR_METADATA_CENTER_REPO}/${PACKAGE_NAME}/${TAGS_PREFIX}/${TAG}.tar.gz

RUN echo ${PACKAGE_URI}

# Download and extract the frontend source
RUN \
curl --fail --show-error --location --remote-name ${PACKAGE_URI} && \
tar --extract --file ${TARBALL} --directory ${CEDAR_FRONTEND_HOME} --strip 1 && \
rm ${TARBALL}

EXPOSE 4300

CMD ["nginx", "-g", "daemon off;"]

ENTRYPOINT [ "/docker-entrypoint.sh" ]
