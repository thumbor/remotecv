#!/usr/bin/python
# -*- coding: utf-8 -*-


import uuid

from redis import RedisError

from tornado.testing import gen_test
from preggy import expect
from thumbor.testing import TestCase

import remotecv.storages.redis_storage


class RedisStorageTestCase(TestCase):
    @gen_test
    async def test_should_be_none_when_not_available(self):
        storage = remotecv.storages.redis_storage.Storage(self.context)
        result = await storage.get_detector_data(uuid.uuid4())
        expect(result).to_be_null()
        self.assertIsNone(result)

    @gen_test
    async def test_should_be_points_when_available(self):
        key = uuid.uuid4()
        storage = remotecv.storages.redis_storage.Storage(self.context)
        await storage.redis_client.set(f"thumbor-detector-{key}", '[{"x": 1}]')
        result = await storage.get_detector_data(key)
        expect(result).to_equal([{"x": 1}])

    @gen_test
    async def test_should_be_error_when_invalid_redis_mode(self):
        self.context.config.REDIS_QUEUE_MODE = "invalid"
        with self.assertRaises(RedisError):
            remotecv.storages.redis_storage.Storage(self.context)

    @gen_test
    async def test_should_be_points_when_available_in_sentinal(self):
        self.context.config.REDIS_QUEUE_MODE = "sentinel"
        self.context.config.REDIS_QUEUE_SENTINEL_INSTANCES = "localhost:26379"
        self.context.config.REDIS_QUEUE_SENTINEL_PASSWORD = None
        self.context.config.REDIS_QUEUE_SENTINEL_MASTER_INSTANCE = (
            "redismaster"
        )
        self.context.config.REDIS_QUEUE_SENTINEL_MASTER_PASSWORD = None
        self.context.config.REDIS_QUEUE_SENTINEL_MASTER_DB = 0

        key = uuid.uuid4()
        storage = remotecv.storages.redis_storage.Storage(self.context)
        await storage.redis_client.set(f"thumbor-detector-{key}", '[{"x": 1}]')
        result = await storage.get_detector_data(key)
        expect(result).to_equal([{"x": 1}])

    @gen_test
    async def test_should_be_points_when_available_in_sentinal_without_auth(
        self,
    ):
        self.context.config.REDIS_QUEUE_MODE = "sentinel"
        self.context.config.REDIS_QUEUE_SENTINEL_INSTANCES = "localhost:26380"
        self.context.config.REDIS_QUEUE_SENTINEL_PASSWORD = "superpassword"
        self.context.config.REDIS_QUEUE_SENTINEL_MASTER_INSTANCE = (
            "redismaster"
        )
        self.context.config.REDIS_QUEUE_SENTINEL_MASTER_PASSWORD = None
        self.context.config.REDIS_QUEUE_SENTINEL_MASTER_DB = 0

        storage = remotecv.storages.redis_storage.Storage(self.context)
        await storage.redis_client.set(
            "thumbor-detector-random_path", '[{"x": 1}]'
        )
        result = await storage.get_detector_data("random_path")
        expect(result).to_equal([{"x": 1}])
