FROM redis:6-alpine

ENV MASTER_INSTANCE redismaster
ENV MASTER_PORT 6380
ENV MASTER_SECURE_INSTANCE redissecuremaster
ENV MASTER_SECURE_PASSWORD superpassword
ENV MASTER_SECURE_PORT 6381
ENV SENTINEL_DOWN_AFTER 1000
ENV SENTINEL_FAILOVER 1000
ENV SENTINEL_PASSWORD superpassword
ENV SENTINEL_QUORUM 2
ENV SLAVE_PORT 6382
ENV SLAVE_SECURE_PORT 6383

RUN mkdir -p /redis

WORKDIR /redis

COPY sentinel.conf .
COPY sentinel-secure.conf .
COPY sentinel-entrypoint.sh /usr/local/bin/

RUN chown redis:redis /redis/* && \
    chmod +x /usr/local/bin/sentinel-entrypoint.sh

EXPOSE 26379
EXPOSE 26380
EXPOSE 6380
EXPOSE 6381
EXPOSE 6382
EXPOSE 6383

ENTRYPOINT ["sentinel-entrypoint.sh"]
