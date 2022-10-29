FROM elasticsearch:6.4.3
# For M1 this would be great, but ES clients only work with 6.x versions at the moment
# elasticsearch     | "stacktrace": ["java.lang.IllegalStateException: Received message from unsupported version: [6.5.3] minimal compatible version is: [6.8.0]",
# FROM elasticsearch:7.17.7

ADD config/elasticsearch.yml /usr/share/elasticsearch/config/

VOLUME /usr/share/elasticsearch/logs
