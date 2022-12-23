#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect
from click.testing import CliRunner

from remotecv import worker


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
