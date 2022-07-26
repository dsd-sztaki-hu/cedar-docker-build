# M1
FROM --platform=linux/arm64 redis:3.2.11

RUN mkdir /log && chown redis:redis /log
VOLUME /log

ADD config/redis.conf /etc/redis/redis.conf

CMD [ "redis-server", "/etc/redis/redis.conf" ]
