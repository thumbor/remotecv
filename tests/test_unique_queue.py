#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock
from urllib.parse import quote

from pyres.job import Job

from remotecv import http_loader
from remotecv.unique_queue import UniqueQueue, UniqueWorker
from remotecv.utils import config, context, redis_client


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
        assert key == "resque:unique:queue:foo:bar"

    def test_should_create_unique_key_spaced(self):
        key = self.unique_queue._create_unique_key("foo", "bar bar")
        assert key == "resque:unique:queue:foo:barbar"

    def test_should_create_unique_key_new_line(self):
        key = self.unique_queue._create_unique_key("foo", "bar\nbar")
        assert key == "resque:unique:queue:foo:barbar"

    def test_should_add_unique_key(self):
        result = self.unique_queue.add_unique_key("foo", "bar")
        assert result

    def test_should_add_unique_key_twice(self):
        result = self.unique_queue.add_unique_key("foo", "bar")
        assert result
        result = self.unique_queue.add_unique_key("foo", "bar")
        assert not result

    def test_should_delete_unique_key(self):
        result = self.unique_queue.add_unique_key("foo", "bar")
        assert result

        self.unique_queue.del_unique_key("foo", "bar")

        value = self.client.get("resque:unique:queue:foo:bar")
        assert value is None

    def test_should_enqueue_from_string(self):
        klass = "foo.bar"
        queue = "foo"
        key = "bar"

        self.unique_queue.enqueue_unique_from_string(klass, queue, key=key)
        value = self.client.get("resque:unique:queue:foo:bar")

        assert value is not None

    def test_should_enqueue_from_string_twice(self):
        klass = "foo.bar"
        queue = "foo"
        key = "bar"

        keys = len(self.client.keys())
        assert keys == 0

        self.unique_queue.enqueue_unique_from_string(klass, queue, key=key)
        value = self.client.get("resque:unique:queue:foo:bar")

        assert value is not None

        self.unique_queue.enqueue_unique_from_string(klass, queue, key=key)
        value = self.client.get("resque:unique:queue:foo:bar")
        queue_value = self.client.llen("resque:queue:foo")
        queues_value = self.client.smembers("resque:queues")

        assert value is not None
        assert queue_value == 1
        assert queues_value == {b"foo"}

    def test_should_not_log_credentials_when_enqueuing(self):
        image_url = quote("http://user:s3cret@images.example.com/a.jpg?sig=x")

        with self.assertLogs("remotecv", level="DEBUG") as logs:
            for _ in range(2):
                self.unique_queue.enqueue_unique_from_string(
                    "remotecv.pyres_tasks.DetectTask",
                    "Detect",
                    args=["all", image_url],
                    key=image_url,
                )

        assert len(logs.output) == 3
        for line in logs.output:
            assert "s3cret" not in line
            assert "sig" not in line

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
        assert self.redis.ttl(f"resque:worker:{str(worker)}:started") == -1

    def test_should_create_unique_worker_with_ttl(self):
        config.worker_ttl = 60
        worker = UniqueWorker(server=self.redis, queues=["Detect"])
        worker.register_worker()
        assert self.redis.ttl(f"resque:worker:{str(worker)}:started") != -1

    def test_should_prune_dead_members_on_startup(self):
        config.prune_dead_members = True
        worker = UniqueWorker(server=self.redis, queues=["Detect"])
        self.redis.sadd("resque:workers", "teste:1:Detect")

        members = self.redis.smembers("resque:workers")
        assert len(members) > 1

        worker.startup()

        members = self.redis.smembers("resque:workers")
        assert len(members) == 1
        assert str(worker).encode() in members

    def test_should_not_prune_dead_members_on_startup(self):
        config.prune_dead_members = False
        worker = UniqueWorker(server=self.redis, queues=["Detect"])
        self.redis.sadd("resque:workers", "teste:1:Detect")

        worker.startup()

        members = self.redis.smembers("resque:workers")
        assert len(members) == 2
        assert str(worker).encode() in members

    def make_job(self, klass):
        payload = {
            "class": klass,
            "queue": "Detect",
            "args": ["all", "http://example.com/image.jpg", "key"],
            "key": "key",
        }
        return Job("Detect", payload, self.unique_queue.resq)

    def test_should_accept_detect_task_before_process(self):
        job = self.make_job("remotecv.pyres_tasks.DetectTask")
        assert self.unique_queue.before_process(job) == job

    def test_should_refuse_unexpected_class_before_process(self):
        self.unique_queue.resq.add_unique_key("Detect", "key")
        job = self.make_job("os.system")

        with self.assertRaisesRegex(ValueError, "os.system"):
            self.unique_queue.before_process(job)

        assert self.redis.get("resque:unique:queue:Detect:key") is None

    def test_should_fail_job_with_unexpected_class(self):
        failed_before = self.redis.llen("resque:failed")

        with mock.patch.object(Job, "perform") as perform:
            self.unique_queue.process(self.make_job("os.system"))

        perform.assert_not_called()
        assert self.redis.llen("resque:failed") == failed_before + 1

    def test_should_not_log_credentials_in_job_args(self):
        self.redis.delete("resque:queue:Detect")
        image_url = quote("http://user:s3cret@images.example.com/a.jpg?sig=x")
        UniqueQueue(server=self.redis).enqueue_unique_from_string(
            "remotecv.pyres_tasks.DetectTask",
            "Detect",
            args=["all", image_url],
            key=image_url,
        )

        with self.assertLogs("pyres.worker", level="INFO") as logs:
            job = self.unique_queue.reserve(timeout=1)

        assert "http://images.example.com/a.jpg" in str(job)
        for text in [str(job), *logs.output]:
            assert "s3cret" not in text
            assert "sig" not in text

    def test_should_reserve_job_with_invalid_url(self):
        self.redis.delete("resque:queue:Detect")
        image_url = quote("http://user:s3cret@[::1/a.jpg?sig=x")
        UniqueQueue(server=self.redis).enqueue_unique_from_string(
            "remotecv.pyres_tasks.DetectTask",
            "Detect",
            args=["all", image_url],
            key=image_url,
        )

        job = self.unique_queue.reserve(timeout=1)

        assert "<invalid url>" in str(job)
        assert "s3cret" not in str(job)

    def test_should_reserve_job_with_unexpected_args(self):
        queue = UniqueQueue(server=self.redis)
        for args in (None, 5):
            self.redis.delete("resque:queue:Detect")
            queue.push(
                "Detect",
                {
                    "class": "remotecv.pyres_tasks.DetectTask",
                    "args": args,
                    "key": "k",
                },
            )

            job = self.unique_queue.reserve(timeout=1)

            assert str(args) in str(job)

    def test_should_not_log_credentials_in_nested_job_args(self):
        self.redis.delete("resque:queue:Detect")
        image_url = "http://user:s3cret@images.example.com/a.jpg?sig=x"
        UniqueQueue(server=self.redis).push(
            "Detect",
            {
                "class": "remotecv.pyres_tasks.DetectTask",
                "args": {"url": image_url, "all": [image_url]},
                "key": "k",
            },
        )

        job = self.unique_queue.reserve(timeout=1)

        assert "http://images.example.com/a.jpg" in str(job)
        assert "s3cret" not in str(job)
        assert "sig" not in str(job)

    def test_should_not_log_credentials_when_job_fails(self):
        config.loader = http_loader
        self.redis.delete("resque:queue:Detect")
        image_url = quote("http://user:s3cret@images.example.com/b.jpg?sig=x")
        UniqueQueue(server=self.redis).enqueue_unique_from_string(
            "remotecv.pyres_tasks.DetectTask",
            "Detect",
            args=["all", image_url],
            key=image_url,
        )
        job = self.unique_queue.reserve(timeout=1)

        with self.assertLogs("pyres.worker", level="ERROR") as logs:
            self.unique_queue.process(job)

        assert "invalid image URL" in logs.output[0]
        for line in logs.output:
            assert "s3cret" not in line
            assert "sig" not in line

    def test_should_flush_sentry_after_a_failed_job(self):
        calls = []
        job = mock.Mock(
            _queue="Detect",
            _payload={"key": "key", "class": "Task", "args": []},
        )
        job.perform.side_effect = RuntimeError("boom")
        job.fail.side_effect = lambda _: calls.append("fail")

        with (
            mock.patch(
                "remotecv.unique_queue.sentry_sdk.flush",
                side_effect=lambda: calls.append("flush"),
            ),
            self.assertLogs("pyres.worker", level="ERROR"),
        ):
            self.unique_queue.process(job)

        assert calls == ["fail", "flush"]
