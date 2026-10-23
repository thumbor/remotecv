#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from click.testing import CliRunner
from preggy import expect

from remotecv import worker
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
        expect(result.exit_code).to_equal(0)
        pyres_mock.assert_called_once()
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_start_celery_worker(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(worker.main, ["-b", "celery"])
        expect(result.exit_code).to_equal(0)
        pyres_mock.assert_not_called()
        celery_mock.assert_called_once()
        http_mock.assert_not_called()

    def test_should_start_healthcheck(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(worker.main, ["--with-healthcheck"])
        expect(result.exit_code).to_equal(0)
        pyres_mock.assert_called_once()
        celery_mock.assert_not_called()
        http_mock.assert_called_once()

    def test_should_refuse_negative_max_image_pixels(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(worker.main, ["--max-image-pixels=-1"])
        expect(result.exit_code).to_equal(2)
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
            expect(result.exit_code).to_equal(2)
        pyres_mock.assert_not_called()
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_refuse_negative_loader_max_body_size(
        self, http_mock, celery_mock, pyres_mock
    ):
        result = self.runner.invoke(
            worker.main, ["--loader-max-body-size", "-1"]
        )
        expect(result.exit_code).to_equal(2)
        pyres_mock.assert_not_called()
        celery_mock.assert_not_called()
        http_mock.assert_not_called()

    def test_should_bind_healthcheck_to_all_interfaces_by_default(
        self, *_mocks
    ):
        self.runner.invoke(worker.main, ["--with-healthcheck"])

        expect(config.server_host).to_equal("0.0.0.0")

    def test_should_read_healthcheck_host_from_option(self, *_mocks):
        self.runner.invoke(worker.main, ["--server-host", "2001:db8::1"])

        expect(config.server_host).to_equal("2001:db8::1")

    def test_should_read_healthcheck_host_from_environment(self, *_mocks):
        self.runner.invoke(worker.main, env={"HTTP_SERVER_HOST": "192.0.2.1"})

        expect(config.server_host).to_equal("192.0.2.1")
