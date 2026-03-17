# -*- coding: utf-8 -*-
# pylint: disable=import-outside-toplevel

import sys
from unittest import TestCase, mock

from preggy import expect

from remotecv.utils import config


class MemcacheStoreTestCase(TestCase):
    def setUp(self):
        config.memcache_hosts = "localhost:11211"
        # Provide a fake pylibmc module so the import inside ResultStore works
        self.pylibmc_mock = mock.MagicMock()
        self.client_mock = mock.MagicMock()
        self.pylibmc_mock.Client.return_value = self.client_mock
        sys.modules["pylibmc"] = self.pylibmc_mock

        # Reset class-level cache between tests
        from remotecv.result_store import memcache_store

        memcache_store.ResultStore.memcache_instance = None

    def tearDown(self):
        sys.modules.pop("pylibmc", None)
        from remotecv.result_store import memcache_store

        memcache_store.ResultStore.memcache_instance = None

    def test_should_create_memcache_client(self):
        from remotecv.result_store.memcache_store import ResultStore

        store = ResultStore(config)

        self.pylibmc_mock.Client.assert_called_once_with(
            ["localhost:11211"],
            binary=True,
            behaviors={"tcp_nodelay": True, "no_block": True, "ketama": True},
        )
        expect(store.storage).to_equal(self.client_mock)

    def test_should_reuse_existing_client(self):
        from remotecv.result_store.memcache_store import ResultStore

        ResultStore(config)
        ResultStore(config)

        expect(self.pylibmc_mock.Client.call_count).to_equal(1)

    def test_should_store_points(self):
        from remotecv.result_store.memcache_store import ResultStore

        store = ResultStore(config)
        store.store("my-key", [[0, 1, 2, 3]])

        self.client_mock.set.assert_called_once()
        call_args = self.client_mock.set.call_args[0]
        expect(call_args[0]).to_equal("thumbor-detector-my-key")
