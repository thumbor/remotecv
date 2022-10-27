
#!/usr/bin/python
# -*- coding: utf-8 -*-

import remotecv.storages.redis_storage

from thumbor.testing import TestCase
from tornado.testing import gen_test

# from unittest.mock import patch, AsyncMock

import asyncio

class RedisStorageTestCase(TestCase):

    @gen_test
    async def test_should_be_none_when_not_available(self):
        storage = remotecv.storages.redis_storage.Storage(self.context)
        result = await storage.get_detector_data("random_path")
        self.assertIsNone(result)

    # @gen_test
    # @patch('remotecv.storages.redis_storage.Storage.redis_client', new=AsyncMock)
    # async def test_should_be_points_when_available(self, redis_mock):
    #     redis_mock.get.return_value = "[{x: 1}]"
    #     storage = remotecv.storages.redis_storage.Storage(self.context)
    #     result = await storage.get_detector_data("random_path")
    #     self.assertIsNone(result)

