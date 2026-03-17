# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.celery_tasks import DETECT_QUEUE, CeleryTasks, CeleryUniqueQueue
from remotecv.utils import config, context, redis_client


def _setup_redis_config():
    config.redis_host = "localhost"
    config.redis_port = 6380
    config.redis_database = 0
    config.redis_password = None
    config.redis_mode = "single_node"
    config.redis_key_expire_time = 1209600


class CeleryUniqueQueueTestCase(TestCase):
    def setUp(self):
        _setup_redis_config()
        context.metrics = mock.Mock()

        self.client = redis_client()
        self.unique_queue = CeleryUniqueQueue(self.client)
        self.client.flushall()

    def test_should_create_unique_key_simple(self):
        key = self.unique_queue._create_unique_key("foo", "bar")
        expect(key).to_equal("celery:unique:queue:foo:bar")

    def test_should_create_unique_key_spaced(self):
        key = self.unique_queue._create_unique_key("foo", "bar bar")
        expect(key).to_equal("celery:unique:queue:foo:barbar")

    def test_should_create_unique_key_new_line(self):
        key = self.unique_queue._create_unique_key("foo", "bar\nbar")
        expect(key).to_equal("celery:unique:queue:foo:barbar")

    def test_should_add_unique_key(self):
        result = self.unique_queue.add_unique_key("foo", "bar")
        expect(result).to_be_true()

    def test_should_add_unique_key_twice(self):
        result = self.unique_queue.add_unique_key("foo", "bar")
        expect(result).to_be_true()
        result = self.unique_queue.add_unique_key("foo", "bar")
        expect(result).to_be_false()

    def test_should_add_unique_key_with_ttl(self):
        self.unique_queue.add_unique_key("foo", "bar")
        ttl = self.client.ttl("celery:unique:queue:foo:bar")
        expect(ttl).to_be_greater_than(0)

    def test_should_add_unique_key_with_configured_ttl(self):
        config.redis_key_expire_time = 60
        self.unique_queue.add_unique_key("foo", "bar")
        ttl = self.client.ttl("celery:unique:queue:foo:bar")
        expect(ttl).to_be_greater_than(0)
        expect(ttl).Not.to_be_greater_than(60)

    def test_should_delete_unique_key(self):
        self.unique_queue.add_unique_key("foo", "bar")
        self.unique_queue.del_unique_key("foo", "bar")
        value = self.client.get("celery:unique:queue:foo:bar")
        expect(value).to_be_null()

    def test_should_send_metrics_on_delete(self):
        context.metrics.reset_mock()
        self.unique_queue.del_unique_key("foo", "bar")
        context.metrics.timing.assert_called_once_with(
            "worker.del_unique_key.time", mock.ANY
        )


class CeleryTasksTestCase(TestCase):
    def setUp(self):
        _setup_redis_config()
        context.metrics = mock.Mock()

        self.client = redis_client()
        self.client.flushall()

    def _make_celery_tasks(self, passthrough_task_decorator=False):
        celery_instance = mock.Mock()
        if passthrough_task_decorator:
            # Make @celery.task(...) return the function unchanged so we can
            # call the task body directly without a broker
            celery_instance.task.return_value = lambda f: f

        with mock.patch(
            "remotecv.celery_tasks.redis_client", return_value=self.client
        ):
            with mock.patch(
                "remotecv.celery_tasks.Celery", return_value=celery_instance
            ):
                return CeleryTasks("key_id", "key_secret", "us-east-1")

    def test_enqueue_unique_calls_apply_async(self):
        celery_tasks = self._make_celery_tasks()
        task_mock = mock.Mock()
        celery_tasks._detect_task = task_mock

        celery_tasks.enqueue_unique("face", "image.jpg", "my-key")

        task_mock.apply_async.assert_called_once_with(
            args=["face", "image.jpg", "my-key"]
        )

    def test_enqueue_unique_sets_redis_key(self):
        celery_tasks = self._make_celery_tasks()
        celery_tasks._detect_task = mock.Mock()

        celery_tasks.enqueue_unique("face", "image.jpg", "my-key")

        value = self.client.get(f"celery:unique:queue:{DETECT_QUEUE}:my-key")
        expect(value).not_to_be_null()

    def test_enqueue_unique_skips_duplicate(self):
        celery_tasks = self._make_celery_tasks()
        task_mock = mock.Mock()
        celery_tasks._detect_task = task_mock

        celery_tasks.enqueue_unique("face", "image.jpg", "my-key")
        celery_tasks.enqueue_unique("face", "image.jpg", "my-key")

        task_mock.apply_async.assert_called_once()

    def test_enqueue_unique_allows_reenqueue_after_task_runs(self):
        celery_tasks = self._make_celery_tasks()
        task_mock = mock.Mock()
        celery_tasks._detect_task = task_mock

        celery_tasks.enqueue_unique("face", "image.jpg", "my-key")
        # Simulate task execution deleting the key before processing
        celery_tasks.unique_queue.del_unique_key(DETECT_QUEUE, "my-key")
        celery_tasks.enqueue_unique("face", "image.jpg", "my-key")

        expect(task_mock.apply_async.call_count).to_equal(2)

    def test_run_commands_without_log_level(self):
        celery_tasks = self._make_celery_tasks()

        celery_tasks.run_commands(["worker"])

        celery_tasks.celery.start.assert_called_once_with(["worker"])
        celery_tasks.celery.conf.update.assert_called_once()  # only BROKER_TRANSPORT_OPTIONS

    def test_run_commands_with_log_level(self):
        celery_tasks = self._make_celery_tasks()

        celery_tasks.run_commands(["worker"], log_level="INFO")

        celery_tasks.celery.conf.update.assert_called_with(
            CELERYD_LOG_LEVEL="INFO"
        )
        celery_tasks.celery.start.assert_called_once_with(["worker"])

    def test_task_deletes_unique_key_on_execution(self):
        celery_tasks = self._make_celery_tasks(passthrough_task_decorator=True)

        # Manually add key as if enqueue_unique was called
        celery_tasks.unique_queue.add_unique_key(DETECT_QUEUE, "my-key")

        with mock.patch("remotecv.celery_tasks.DetectTask") as detect_mock:
            detect_mock.perform = mock.Mock()
            # Call the task body directly, bypassing Celery broker
            task_fn = celery_tasks.get_detect_task()
            task_fn("face", "image.jpg", "my-key")

        value = self.client.get(f"celery:unique:queue:{DETECT_QUEUE}:my-key")
        expect(value).to_be_null()
