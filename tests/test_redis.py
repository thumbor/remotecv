# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.utils import config, context, redis_client


class RedisSingleNodeClientTestCase(TestCase):
    def setUp(self):
        context.metrics = mock.Mock()

    def test_should_connect_to_redis_single_node(self):
        config.redis_host = "localhost"
        config.redis_port = 6379
        config.redis_database = 0
        config.redis_password = "superpassword"
        config.redis_mode = "single_node"

        client = redis_client()

        expect(client).not_to_be_null()
        connection_kwargs = client.connection_pool.connection_kwargs
        expect(connection_kwargs["host"]).to_equal("localhost")
        expect(connection_kwargs["port"]).to_equal(6379)
        expect(connection_kwargs["db"]).to_equal(0)
        expect(connection_kwargs["password"]).to_equal("superpassword")

    def test_should_connect_to_redis_single_node_no_pass(self):
        config.redis_host = "localhost"
        config.redis_port = 6380
        config.redis_database = 0
        config.redis_password = None
        config.redis_mode = "single_node"

        client = redis_client()

        expect(client).not_to_be_null()
        connection_kwargs = client.connection_pool.connection_kwargs
        expect(connection_kwargs["host"]).to_equal("localhost")
        expect(connection_kwargs["port"]).to_equal(6380)
        expect(connection_kwargs["db"]).to_equal(0)
        expect(connection_kwargs["password"]).to_be_null()


class RedisSentinelClientTestCase(TestCase):
    def setUp(self):
        context.metrics = mock.Mock()

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
        connection_pool = client.connection_pool
        expect(connection_pool.service_name).to_equal("redismaster")
        expect(connection_pool.is_master).to_be_true()
        expect(connection_pool.connection_kwargs["db"]).to_equal(0)
        expect(connection_pool.connection_kwargs["password"]).to_be_null()

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
        connection_pool = client.connection_pool
        expect(connection_pool.service_name).to_equal("redismaster")
        expect(connection_pool.is_master).to_be_true()
        expect(connection_pool.connection_kwargs["db"]).to_equal(0)
        expect(connection_pool.connection_kwargs["password"]).to_be_null()


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
