# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from remotecv.utils import config, context, redis_client


class RedisSingleNodeClientTestCase(TestCase):
    def test_should_connect_to_redis_single_node(self):
        config.redis_host = "localhost"
        config.redis_port = 6379
        config.redis_database = 0
        config.redis_password = "superpassword"
        config.redis_mode = "single_node"

        client = redis_client()

        assert client is not None
        connection_kwargs = client.connection_pool.connection_kwargs
        assert connection_kwargs["host"] == "localhost"
        assert connection_kwargs["port"] == 6379
        assert connection_kwargs["db"] == 0
        assert connection_kwargs["password"] == "superpassword"

    def test_should_connect_to_redis_single_node_no_pass(self):
        config.redis_host = "localhost"
        config.redis_port = 6380
        config.redis_database = 0
        config.redis_password = None
        config.redis_mode = "single_node"

        client = redis_client()

        assert client is not None
        connection_kwargs = client.connection_pool.connection_kwargs
        assert connection_kwargs["host"] == "localhost"
        assert connection_kwargs["port"] == 6380
        assert connection_kwargs["db"] == 0
        assert connection_kwargs["password"] is None


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

        assert client is not None
        connection_pool = client.connection_pool
        assert connection_pool.service_name == "redismaster"
        assert connection_pool.is_master
        assert connection_pool.connection_kwargs["db"] == 0
        assert connection_pool.connection_kwargs["password"] is None

    def test_should_connect_to_redis_sentinel_no_pass(self):
        config.redis_mode = "sentinel"
        config.redis_sentinel_instances = "localhost:26379"
        config.redis_sentinel_password = None
        config.redis_sentinel_master_instance = "redismaster"
        config.redis_sentinel_master_password = None
        config.redis_sentinel_master_database = 0
        config.redis_sentinel_socket_timeout = 10.0

        client = redis_client()

        assert client is not None
        connection_pool = client.connection_pool
        assert connection_pool.service_name == "redismaster"
        assert connection_pool.is_master
        assert connection_pool.connection_kwargs["db"] == 0
        assert connection_pool.connection_kwargs["password"] is None


class RedisNoneClientTestCase(TestCase):
    def test_should_return_none(self):
        config.redis_mode = None

        with self.assertRaises(AttributeError) as err:
            redis_client()

        assert (
            str(err.exception)
            == "redis-mode must be either single_node or sentinel"
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
        assert client is not None

        context.metrics.timing.assert_any_call(
            "worker.redis_connection.time", mock.ANY
        )
