#!/bin/sh

sed -i "s/MASTER_INSTANCE/$MASTER_INSTANCE/g" /redis/sentinel.conf
sed -i "s/MASTER_PORT/$MASTER_PORT/g" /redis/sentinel.conf
sed -i "s/SENTINEL_DOWN_AFTER/$SENTINEL_DOWN_AFTER/g" /redis/sentinel.conf
sed -i "s/SENTINEL_FAILOVER/$SENTINEL_FAILOVER/g" /redis/sentinel.conf
sed -i "s/SENTINEL_QUORUM/$SENTINEL_QUORUM/g" /redis/sentinel.conf

sed -i "s/MASTER_INSTANCE/$MASTER_INSTANCE/g" /redis/sentinel-secure.conf
sed -i "s/MASTER_PORT/$MASTER_PORT/g" /redis/sentinel-secure.conf
sed -i "s/SENTINEL_DOWN_AFTER/$SENTINEL_DOWN_AFTER/g" /redis/sentinel-secure.conf
sed -i "s/SENTINEL_FAILOVER/$SENTINEL_FAILOVER/g" /redis/sentinel-secure.conf
sed -i "s/SENTINEL_PASSWORD/$SENTINEL_PASSWORD/g" /redis/sentinel-secure.conf
sed -i "s/SENTINEL_QUORUM/$SENTINEL_QUORUM/g" /redis/sentinel-secure.conf

# Master
redis-server --port $MASTER_PORT &

# Slave
redis-server --port $SLAVE_PORT --slaveof localhost $MASTER_PORT &

# Sentinel
redis-server /redis/sentinel.conf --sentinel &
redis-server /redis/sentinel-secure.conf --sentinel &

wait -n
