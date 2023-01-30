# pataki@: the originally used 3.5.3 was based on Alpine and its java didn't start at all. Now switched to
# 3.5.6 (by trial and error), which is debian based and using apt-get instead of apk and it seems to start up all right
FROM --platform=linux/amd64 neo4j:3.5.6

# RUN apk --no-cache add curl netcat-openbsd
# M1
RUN apt-get install curl netcat-openbsd

WORKDIR /var/lib/neo4j

RUN mkdir /state

VOLUME /logs
VOLUME /state

ADD scripts/docker-entrypoint-wrapper.sh /docker-entrypoint-wrapper.sh
ADD scripts/neo4j-init.sh /neo4j-init.sh
ADD config/neo4j-create-cedar-admin.json /neo4j-create-cedar-admin.json

ENTRYPOINT ["/docker-entrypoint-wrapper.sh"]
CMD ["neo4j"]
