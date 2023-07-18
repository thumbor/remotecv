#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.unique_queue import UniqueQueue, UniqueWorker
from remotecv.utils import context, config, redis_client


class UniqueQueueTestCase(TestCase):
    def setUp(self):
        config.redis_host = "localhost"
        config.redis_port = 6380
        config.redis_database = 0
        config.redis_password = None
        config.redis_mode = "single_node"

        self.client = redis_client()
        self.unique_queue = UniqueQueue(server=self.client)
        self.client.flushall()

    def test_should_create_unique_key_simple(self):
        key = self.unique_queue._create_unique_key("foo", "bar")
        expect(key).to_equal("resque:unique:queue:foo:bar")

    def test_should_create_unique_key_spaced(self):
        key = self.unique_queue._create_unique_key("foo", "bar bar")
        expect(key).to_equal("resque:unique:queue:foo:barbar")

    def test_should_create_unique_key_new_line(self):
        key = self.unique_queue._create_unique_key("foo", "bar\nbar")
        expect(key).to_equal("resque:unique:queue:foo:barbar")

    def test_should_add_unique_key(self):
        result = self.unique_queue.add_unique_key("foo", "bar")
        expect(result).to_be_true()

    def test_should_add_unique_key_twice(self):
        result = self.unique_queue.add_unique_key("foo", "bar")
        expect(result).to_be_true()
        result = self.unique_queue.add_unique_key("foo", "bar")
        expect(result).to_be_false()

    def test_should_delete_unique_key(self):
        result = self.unique_queue.add_unique_key("foo", "bar")
        expect(result).to_be_true()

        self.unique_queue.del_unique_key("foo", "bar")

        value = self.client.get("resque:unique:queue:foo:bar")
        expect(value).to_be_null()

    def test_should_enqueue_from_string(self):
        klass = "foo.bar"
        queue = "foo"
        key = "bar"

        self.unique_queue.enqueue_unique_from_string(klass, queue, key=key)
        value = self.client.get("resque:unique:queue:foo:bar")

        expect(value).Not.to_be_null()

    def test_should_enqueue_from_string_twice(self):
        klass = "foo.bar"
        queue = "foo"
        key = "bar"

        keys = len(self.client.keys())
        expect(keys).to_equal(0)

        self.unique_queue.enqueue_unique_from_string(klass, queue, key=key)
        value = self.client.get("resque:unique:queue:foo:bar")

        expect(value).not_to_be_null()

        self.unique_queue.enqueue_unique_from_string(klass, queue, key=key)
        value = self.client.get("resque:unique:queue:foo:bar")
        queue_value = self.client.llen("resque:queue:foo")
        queues_value = self.client.smembers("resque:queues")

        expect(value).not_to_be_null()
        expect(queue_value).to_equal(1)
        expect(queues_value).to_equal({b"foo"})

    def test_should_send_metrics(self):
        context.metrics = mock.Mock()
        self.unique_queue.del_unique_key("foo", "bar")

        context.metrics.timing.assert_called_once_with(
            "worker.del_unique_key.time", mock.ANY
        )


class UniqueWorkerTestCase(TestCase):
    def setUp(self):
        self.redis = redis_client()
        self.unique_queue = UniqueWorker(
            queues=["Detect"],
            server=self.redis,
            timeout=None,
        )

    def test_should_send_queue_metrics(self):
        context.metrics = mock.Mock()
        self.unique_queue.reserve(timeout=1)

        context.metrics.timing.assert_called_once_with(
            "worker.read_queue.time", mock.ANY
        )

    def test_should_create_unique_worker_without_ttl(self):
        config.worker_ttl = None
        worker = UniqueWorker(server=self.redis, queues=["Detect"])
        worker.register_worker()
        expect(
            self.redis.ttl(f"resque:worker:{str(worker)}:started")
        ).to_equal(-1)

    def test_should_create_unique_worker_with_ttl(self):
        config.worker_ttl = 60
        worker = UniqueWorker(server=self.redis, queues=["Detect"])
        worker.register_worker()
        expect(
            self.redis.ttl(f"resque:worker:{str(worker)}:started")
        ).Not.to_equal(-1)
