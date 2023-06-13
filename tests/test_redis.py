#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.utils import context, config, redis_client


class RedisSingleNodeClientTestCase(TestCase):
    def test_should_connect_to_redis_single_node(self):
        config.redis_host = "localhost"
        config.redis_port = 6379
        config.redis_database = 0
        config.redis_password = "superpassword"
        config.redis_mode = "single_node"

        client = redis_client()

        expect(client).not_to_be_null()
        expect(str(client)).to_equal(
            "Redis<ConnectionPool<Connection<host=localhost,port=6379,db=0>>>"
        )

    def test_should_connect_to_redis_single_node_no_pass(self):
        config.redis_host = "localhost"
        config.redis_port = 6380
        config.redis_database = 0
        config.redis_password = None
        config.redis_mode = "single_node"

        client = redis_client()
        expect(client).not_to_be_null()
        expect(str(client)).to_equal(
            "Redis<ConnectionPool<Connection<host=localhost,port=6380,db=0>>>"
        )


class RedisSentinelClientTestCase(TestCase):
    def test_should_connect_to_redis_sentinel(self):
        config.redis_mode = "sentinel"
        config.redis_sentinel_instances = "localhost:26380"
        config.redis_sentinel_password = "superpassword"
        config.redis_sentinel_master_instance = "redismaster"
        config.redis_sentinel_master_password = None
        config.redis_sentinel_master_database = 0
        config.redis_sentinel_socket_timeout = 10.0

        client = redis_client()
        expect(client).not_to_be_null()
        expect(str(client)).to_equal(
            "Redis<SentinelConnectionPool<service=redismaster(master)>"
        )

    def test_should_connect_to_redis_sentinel_no_pass(self):
        config.redis_mode = "sentinel"
        config.redis_sentinel_instances = "localhost:26379"
        config.redis_sentinel_password = None
        config.redis_sentinel_master_instance = "redismaster"
        config.redis_sentinel_master_password = None
        config.redis_sentinel_master_database = 0
        config.redis_sentinel_socket_timeout = 10.0

        client = redis_client()
        expect(client).not_to_be_null()
        expect(str(client)).to_equal(
            "Redis<SentinelConnectionPool<service=redismaster(master)>"
        )


class RedisNoneClientTestCase(TestCase):
    def test_should_return_none(self):
        config.redis_mode = None

        with self.assertRaises(AttributeError) as err:
            redis_client()

        expect(str(err.exception)).to_equal(
            "redis-mode must be either single_node or sentinel"
        )


class RedisConnectionMetricsTestCase(TestCase):
    def test_should_send_redis_connection_metrics(self):
        config.redis_host = "localhost"
        config.redis_port = 6379
        config.redis_database = 0
        config.redis_password = "superpassword"
        config.redis_mode = "single_node"
        context.metrics = mock.Mock()

        client = redis_client()
        expect(client).not_to_be_null()

        context.metrics.timing.assert_any_call(
            "worker.redis_connection.time", mock.ANY
        )
