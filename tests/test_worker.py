# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from click.testing import CliRunner
from kombu import Connection

from remotecv import worker
from remotecv.http_loader import DEFAULT_USER_AGENT
from remotecv.utils import config


@mock.patch("remotecv.worker.start_celery_worker")
@mock.patch("remotecv.worker.start_http_server")
class WorkerTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        find_spec_patcher = mock.patch(
            "remotecv.worker.find_spec", return_value=mock.Mock()
        )
        find_spec_patcher.start()
        self.addCleanup(find_spec_patcher.stop)

    def test_should_start_celery_worker(self, http_mock, celery_mock):
        result = self.runner.invoke(worker.main)
        assert result.exit_code == 0
        celery_mock.assert_called_once()
        http_mock.assert_not_called()

    def test_should_default_to_redis_broker(self, _http_mock, _celery_mock):
        result = self.runner.invoke(worker.main)
        assert result.exit_code == 0
        assert config.broker_url == "redis://localhost:6379/0"

    def test_should_refuse_legacy_backend_env(self, _http_mock, celery_mock):
        result = self.runner.invoke(worker.main, env={"BACKEND": "pyres"})
        assert result.exit_code == 2
        assert "BACKEND is no longer supported" in result.output
        celery_mock.assert_not_called()

    def test_should_refuse_negative_timeout(self, http_mock, celery_mock):
        result = self.runner.invoke(worker.main, ["--timeout", "-1"])
        assert result.exit_code == 2
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_start_healthcheck(self, http_mock, celery_mock):
        result = self.runner.invoke(worker.main, ["--with-healthcheck"])
        assert result.exit_code == 0
        celery_mock.assert_called_once()
        http_mock.assert_called_once()

    def test_should_refuse_negative_max_image_pixels(
        self, http_mock, celery_mock
    ):
        result = self.runner.invoke(worker.main, ["--max-image-pixels=-1"])
        assert result.exit_code == 2
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_refuse_invalid_loader_timeout(
        self, http_mock, celery_mock
    ):
        for value in ("0", "-1", "nan", "inf", "1e400"):
            result = self.runner.invoke(
                worker.main, ["--loader-timeout", value]
            )
            assert result.exit_code == 2
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_refuse_negative_loader_max_body_size(
        self, http_mock, celery_mock
    ):
        result = self.runner.invoke(
            worker.main, ["--loader-max-body-size", "-1"]
        )
        assert result.exit_code == 2
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_send_remotecv_user_agent_by_default(self, *_mocks):
        self.runner.invoke(worker.main)

        assert config.loader_user_agent == DEFAULT_USER_AGENT

    def test_should_read_loader_user_agent_from_env(self, *_mocks):
        self.runner.invoke(
            worker.main, env={"IMAGE_LOADER_USER_AGENT": "Thumbor/7.8.0"}
        )

        assert config.loader_user_agent == "Thumbor/7.8.0"

    def test_should_refuse_invalid_loader_user_agent(
        self, http_mock, celery_mock
    ):
        for value in ("", "a\r\nX-Injected: 1", "a\tb", "caf\u00e9"):
            result = self.runner.invoke(
                worker.main, ["--loader-user-agent", value]
            )
            assert result.exit_code == 2
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_bind_healthcheck_to_all_interfaces_by_default(
        self, *_mocks
    ):
        self.runner.invoke(worker.main, ["--with-healthcheck"])

        assert config.server_host == "0.0.0.0"

    def test_should_read_healthcheck_host_from_option(self, *_mocks):
        self.runner.invoke(worker.main, ["--server-host", "2001:db8::1"])

        assert config.server_host == "2001:db8::1"

    def test_should_read_healthcheck_host_from_environment(self, *_mocks):
        self.runner.invoke(worker.main, env={"HTTP_SERVER_HOST": "192.0.2.1"})

        assert config.server_host == "192.0.2.1"

    def test_should_configure_sqs_broker(self, _http_mock, _celery_mock):
        result = self.runner.invoke(
            worker.main,
            [
                "--broker=sqs",
                "--key-id=key",
                "--key-secret=secret",
                "--region=sa-east-1",
                "--timeout=30",
            ],
        )
        assert result.exit_code == 0
        assert config.broker_url == "sqs://key:secret@"
        assert config.broker_transport_options == {
            "region": "sa-east-1",
            "visibility_timeout": 30,
            "polling_interval": 20,
            "queue_name_prefix": "celery-remotecv-",
        }

    def test_should_configure_sqs_broker_without_keys(
        self, _http_mock, _celery_mock
    ):
        result = self.runner.invoke(
            worker.main,
            ["--broker=sqs"],
            env={"AWS_ACCESS_KEY_ID": None, "AWS_SECRET_ACCESS_KEY": None},
        )
        assert result.exit_code == 0
        assert config.broker_url == "sqs://"

    def test_should_refuse_sqs_key_id_without_secret(
        self, _http_mock, celery_mock
    ):
        result = self.runner.invoke(
            worker.main,
            ["--broker=sqs", "--key-id=key"],
            env={"AWS_SECRET_ACCESS_KEY": None},
        )
        assert result.exit_code == 2
        assert "must be set together" in result.output
        celery_mock.assert_not_called()

    def test_should_refuse_sqs_broker_without_sqs_extra(
        self, _http_mock, celery_mock
    ):
        with mock.patch("remotecv.worker.find_spec", return_value=None):
            result = self.runner.invoke(worker.main, ["--broker=sqs"])
        assert result.exit_code == 2
        assert "pip install 'remotecv[sqs]'" in result.output
        celery_mock.assert_not_called()


class StartCeleryWorkerTestCase(TestCase):
    def setUp(self):
        config.broker_url = "redis://localhost:6379/0"
        config.broker_transport_options = None
        config.extra_args = ["worker"]
        config.log_level = "INFO"
        config.timeout = 30

    @mock.patch("remotecv.worker.redis_client")
    @mock.patch("remotecv.worker.CeleryUniqueQueue")
    @mock.patch("remotecv.worker.CeleryTasks")
    def test_should_call_run_commands(
        self, celery_tasks_mock, unique_queue_mock, redis_client_mock
    ):
        instance = mock.Mock()
        celery_tasks_mock.return_value = instance

        worker.start_celery_worker()

        unique_queue_mock.assert_called_once_with(
            redis_client_mock.return_value
        )
        celery_tasks_mock.assert_called_once_with(
            config.broker_url,
            config.broker_transport_options,
            unique_queue=unique_queue_mock.return_value,
            time_limit=30,
        )
        instance.run_commands.assert_called_once_with(
            config.extra_args, log_level=config.log_level
        )


class BuildRedisBrokerTestCase(TestCase):
    def setUp(self):
        config.redis_mode = "single_node"
        config.redis_host = "localhost"
        config.redis_port = 6379
        config.redis_database = 0
        config.redis_password = None
        config.redis_sentinel_instances = "localhost:26379"
        config.redis_sentinel_password = None
        config.redis_sentinel_master_instance = "redismaster"
        config.redis_sentinel_master_password = None
        config.redis_sentinel_master_database = 0

    def test_should_build_single_node_url(self):
        config.redis_database = 2

        url = worker._build_redis_broker_url()

        assert url == "redis://localhost:6379/2"
        assert worker._build_redis_broker_transport_options() is None

    def test_should_quote_single_node_password(self):
        config.redis_password = "p@ss/w#rd%41"

        connection = Connection(worker._build_redis_broker_url())

        assert connection.hostname == "localhost"
        assert connection.password == "p@ss/w#rd%41"
        assert connection.virtual_host == "0"

    def test_should_prefix_every_sentinel_instance(self):
        config.redis_mode = "sentinel"
        config.redis_sentinel_instances = "sentinel-1:26379,sentinel-2:26380"
        config.redis_sentinel_master_password = "p@ss"
        config.redis_sentinel_master_database = 3

        url = worker._build_redis_broker_url()

        assert (
            url == "sentinel://:p%40ss@sentinel-1:26379/3;"
            "sentinel://:p%40ss@sentinel-2:26380/3"
        )

    def test_should_build_sentinel_transport_options(self):
        config.redis_mode = "sentinel"
        config.redis_sentinel_password = "superpassword"

        options = worker._build_redis_broker_transport_options()

        assert options == {
            "master_name": "redismaster",
            "sentinel_kwargs": {"password": "superpassword"},
        }

    def test_should_fail_over_to_next_sentinel(self):
        config.redis_mode = "sentinel"
        config.redis_sentinel_instances = "localhost:26999,localhost:26379"
        config.redis_sentinel_master_database = 3

        with Connection(
            worker._build_redis_broker_url(),
            transport_options=worker._build_redis_broker_transport_options(),
        ) as connection:
            client = connection.default_channel.client

            assert client.ping()
            assert client.connection_pool.connection_kwargs["db"] == 3
