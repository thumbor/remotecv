# -*- coding: utf-8 -*-

from unittest import TestCase, mock
from urllib.parse import quote

from kombu.exceptions import OperationalError
from kombu.utils.url import parse_url
from preggy import expect
from redis.exceptions import ConnectionError as RedisConnectionError

from remotecv.celery_tasks import (
    DETECT_QUEUE,
    CeleryTasks,
    CeleryUniqueQueue,
    build_sqs_broker,
)
from remotecv.utils import config, context, redis_client


def _setup_redis_config():
    config.redis_host = "localhost"
    config.redis_port = 6380
    config.redis_database = 0
    config.redis_password = None
    config.redis_mode = "single_node"


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
        unique_queue = CeleryUniqueQueue(self.client, expire_time=60)
        unique_queue.add_unique_key("foo", "bar")
        ttl = self.client.ttl("celery:unique:queue:foo:bar")
        expect(ttl).to_be_greater_than(0)
        expect(ttl).Not.to_be_greater_than(60)

    def test_should_delete_unique_key(self):
        self.unique_queue.add_unique_key("foo", "bar")
        self.unique_queue.del_unique_key("foo", "bar")
        value = self.client.get("celery:unique:queue:foo:bar")
        expect(value).to_be_null()

    def test_should_delete_unique_key_without_metrics_context(self):
        self.unique_queue.add_unique_key("foo", "bar")
        with mock.patch.object(context, "metrics", None):
            self.unique_queue.del_unique_key("foo", "bar")
        expect(self.client.exists("celery:unique:queue:foo:bar")).to_equal(0)


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
            "remotecv.celery_tasks.Celery", return_value=celery_instance
        ):
            return CeleryTasks(
                "redis://localhost:6380/0",
                unique_queue=CeleryUniqueQueue(self.client),
            )

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

    def test_enqueue_unique_does_not_log_credentials(self):
        celery_tasks = self._make_celery_tasks()
        celery_tasks._detect_task = mock.Mock()
        image_url = quote("http://user:s3cret@images.example.com/a.jpg?sig=x")

        with self.assertLogs("remotecv", level="DEBUG") as logs:
            for _ in range(2):
                celery_tasks.enqueue_unique("all", image_url, image_url)

        expect(logs.output).to_length(2)
        for line in logs.output:
            expect(line).Not.to_include("s3cret")
            expect(line).Not.to_include("sig")

    def test_run_commands_without_log_level(self):
        celery_tasks = self._make_celery_tasks()

        celery_tasks.run_commands(["worker"])

        celery_tasks.celery.start.assert_called_once_with(["worker"])
        celery_tasks.celery.conf.update.assert_not_called()

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
        context.metrics.timing.assert_any_call(
            "worker.del_unique_key.time", mock.ANY
        )

    def test_enqueue_unique_releases_key_when_publish_fails(self):
        celery_tasks = self._make_celery_tasks()
        task_mock = mock.Mock()
        task_mock.apply_async.side_effect = OperationalError("broker down")
        celery_tasks._detect_task = task_mock

        with self.assertRaises(OperationalError):
            celery_tasks.enqueue_unique("face", "image.jpg", "my-key")

        value = self.client.get(f"celery:unique:queue:{DETECT_QUEUE}:my-key")
        expect(value).to_be_null()

        task_mock.apply_async.side_effect = None
        celery_tasks.enqueue_unique("face", "image.jpg", "my-key")
        expect(task_mock.apply_async.call_count).to_equal(2)

    def test_task_without_unique_queue_still_detects(self):
        celery_instance = mock.Mock()
        celery_instance.task.return_value = lambda f: f
        with mock.patch(
            "remotecv.celery_tasks.Celery", return_value=celery_instance
        ):
            celery_tasks = CeleryTasks("redis://localhost:6380/0")

        with mock.patch("remotecv.celery_tasks.DetectTask") as detect_mock:
            celery_tasks.get_detect_task()("face", "image.jpg", "my-key")

        detect_mock.perform.assert_called_once_with(
            "face", "image.jpg", "my-key"
        )

    def test_task_detects_when_unique_key_release_fails(self):
        redis_mock = mock.Mock()
        redis_mock.delete.side_effect = RedisConnectionError("down")
        celery_instance = mock.Mock()
        celery_instance.task.return_value = lambda f: f
        with mock.patch(
            "remotecv.celery_tasks.Celery", return_value=celery_instance
        ):
            celery_tasks = CeleryTasks(
                "sqs://key:secret@",
                unique_queue=CeleryUniqueQueue(redis_mock),
            )

        with mock.patch("remotecv.celery_tasks.DetectTask") as detect_mock:
            with self.assertLogs("remotecv", level="WARNING") as logs:
                celery_tasks.get_detect_task()("face", "image.jpg", "my-key")

        detect_mock.perform.assert_called_once_with(
            "face", "image.jpg", "my-key"
        )
        expect(logs.output[0]).to_include("could not release unique key")

    def test_task_does_not_log_credentials_when_unique_key_release_fails(
        self,
    ):
        redis_mock = mock.Mock()
        redis_mock.delete.side_effect = RedisConnectionError("down")
        celery_instance = mock.Mock()
        celery_instance.task.return_value = lambda f: f
        with mock.patch(
            "remotecv.celery_tasks.Celery", return_value=celery_instance
        ):
            celery_tasks = CeleryTasks(
                "sqs://key:secret@",
                unique_queue=CeleryUniqueQueue(redis_mock),
            )
        image_url = quote("http://user:s3cret@images.example.com/a.jpg?sig=x")

        with mock.patch("remotecv.celery_tasks.DetectTask"):
            with self.assertLogs("remotecv", level="WARNING") as logs:
                celery_tasks.get_detect_task()("all", image_url, image_url)

        expect(logs.output[0]).to_include("images.example.com/a.jpg")
        expect(logs.output[0]).Not.to_include("s3cret")
        expect(logs.output[0]).Not.to_include("sig")

    def test_task_uses_time_limit(self):
        celery_tasks = CeleryTasks("memory://", time_limit=30)

        expect(celery_tasks.get_detect_task().time_limit).to_equal(30)

    def test_task_has_no_time_limit_by_default(self):
        celery_tasks = CeleryTasks("memory://")

        expect(celery_tasks.get_detect_task().time_limit).to_be_null()


class BuildSqsBrokerTestCase(TestCase):
    def test_should_build_url_and_transport_options(self):
        url, options = build_sqs_broker("key", "secret", "sa-east-1", 30, 5)

        expect(url).to_equal("sqs://key:secret@")
        expect(options).to_equal(
            {
                "region": "sa-east-1",
                "visibility_timeout": 30,
                "polling_interval": 5,
                "queue_name_prefix": "celery-remotecv-",
            }
        )

    def test_should_use_default_timeouts(self):
        _, options = build_sqs_broker("key", "secret", "us-east-1")

        expect(options["visibility_timeout"]).to_equal(120)
        expect(options["polling_interval"]).to_equal(20)

    def test_should_leave_credentials_to_boto3_when_keys_are_unset(self):
        url, _ = build_sqs_broker(None, None, "us-east-1")

        expect(url).to_equal("sqs://")
        expect(parse_url(url)["userid"]).to_be_null()
        expect(parse_url(url)["password"]).to_be_null()

    def test_should_quote_credentials(self):
        url, _ = build_sqs_broker("AKIA/ID", "abc/def+ghi", "us-east-1")

        expect(parse_url(url)["userid"]).to_equal("AKIA/ID")
        expect(parse_url(url)["password"]).to_equal("abc/def+ghi")

    def test_should_require_key_id_and_secret_together(self):
        with self.assertRaises(ValueError):
            build_sqs_broker("key", None, "us-east-1")
        with self.assertRaises(ValueError):
            build_sqs_broker(None, "secret", "us-east-1")
