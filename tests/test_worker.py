#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from click.testing import CliRunner

from remotecv import worker
from remotecv.http_loader import DEFAULT_USER_AGENT
from remotecv.utils import config


@mock.patch("remotecv.worker.start_pyres_worker")
@mock.patch("remotecv.worker.start_celery_worker")
@mock.patch("remotecv.worker.start_http_server")
class UniqueQueueTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_should_start_pyres_worker(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(worker.main)
        assert result.exit_code == 0
        pyres_mock.assert_called_once()
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_start_celery_worker(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(worker.main, ["-b", "celery"])
        assert result.exit_code == 0
        pyres_mock.assert_not_called()
        celery_mock.assert_called_once()
        http_mock.assert_not_called()

    def test_should_refuse_negative_timeout(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(
            worker.main, ["-b", "celery", "--timeout", "-1"]
        )
        assert result.exit_code == 2
        celery_mock.assert_not_called()
        pyres_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_start_healthcheck(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(worker.main, ["--with-healthcheck"])
        assert result.exit_code == 0
        pyres_mock.assert_called_once()
        celery_mock.assert_not_called()
        http_mock.assert_called_once()

    def test_should_refuse_negative_max_image_pixels(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(worker.main, ["--max-image-pixels=-1"])
        assert result.exit_code == 2
        pyres_mock.assert_not_called()
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_refuse_invalid_loader_timeout(
        self, http_mock, celery_mock, pyres_mock
    ):
        for value in ("0", "-1", "nan", "inf", "1e400"):
            result = self.runner.invoke(
                worker.main, ["--loader-timeout", value]
            )
            assert result.exit_code == 2
        pyres_mock.assert_not_called()
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_refuse_negative_loader_max_body_size(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(
            worker.main, ["--loader-max-body-size", "-1"]
        )
        assert result.exit_code == 2
        pyres_mock.assert_not_called()
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
        self, http_mock, celery_mock, pyres_mock
    ):
        for value in ("", "a\r\nX-Injected: 1", "a\tb", "caf\u00e9"):
            result = self.runner.invoke(
                worker.main, ["--loader-user-agent", value]
            )
            assert result.exit_code == 2
        pyres_mock.assert_not_called()
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
