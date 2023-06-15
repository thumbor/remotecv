#!/usr/bin/python
# -*- coding: utf-8 -*-


import time

from thumbor.testing import TestCase
from tornado.testing import gen_test
from preggy import expect

from remotecv.result_store.redis_store import ResultStore
from remotecv.utils import config, redis_client


class RedisStorageTestCase(TestCase):
    @gen_test
    async def test_should_be_none_when_not_available(self):
        config.redis_host = "localhost"
        config.redis_port = 6379
        config.redis_database = 0
        config.redis_password = None
        config.redis_mode = "single_node"
        config.redis_key_expire_time = 2
        points = [[0, 1, 2, 3], [0, 2, 3, 4]]
        client = redis_client()

        result_store = ResultStore(config)

        value = client.get("thumbor-detector-key")
        expect(value).to_be_null()

        result_store.store("key", points)

        value = client.get("thumbor-detector-key")
        points_serialized = (b'[{"x": 1.0, "y": 2.5, "height": 2,' +
                             b' "width": 3, "origin": "", "z": 6},' +
                             b' {"x": 1.5, "y": 4.0, ' +
                             b'"height": 3, "width": 4, ' +
                             b'"origin": "", "z": 12}]')
        expect(value).to_equal(points_serialized)

        time.sleep(3)

        value = client.get("thumbor-detector-key")
        expect(value).to_be_null()
