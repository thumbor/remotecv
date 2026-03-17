# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from click.testing import CliRunner
from preggy import expect

from remotecv import worker
from remotecv.utils import config, context


@mock.patch("remotecv.worker.start_celery_worker")
@mock.patch("remotecv.worker.start_http_server")
class WorkerTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_should_start_celery_worker(self, http_mock, celery_mock):
        result = self.runner.invoke(worker.main)
        expect(result.exit_code).to_equal(0)
        celery_mock.assert_called_once()
        http_mock.assert_not_called()

    def test_should_start_healthcheck(self, http_mock, celery_mock):
        result = self.runner.invoke(worker.main, ["--with-healthcheck"])
        expect(result.exit_code).to_equal(0)
        celery_mock.assert_called_once()
        http_mock.assert_called_once()


class StartCeleryWorkerTestCase(TestCase):
    def setUp(self):
        context.metrics = mock.Mock()
        config.broker_url = "redis://localhost:6379/0"
        config.broker_transport_options = None
        config.extra_args = ["worker"]
        config.log_level = "INFO"

    @mock.patch("remotecv.celery_tasks.CeleryTasks")
    def test_should_call_run_commands(self, celery_tasks_mock):
        instance = mock.Mock()
        celery_tasks_mock.return_value = instance

        worker.start_celery_worker()

        celery_tasks_mock.assert_called_once_with(
            config.broker_url,
            config.broker_transport_options,
        )
        instance.run_commands.assert_called_once_with(
            config.extra_args, log_level=config.log_level
        )
