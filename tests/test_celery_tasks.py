# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from unittest import TestCase

from remotecv.celery_tasks import CeleryTasks, broker_url


class BrokerUrlTestCase(TestCase):
    def test_should_quote_credentials(self):
        url = broker_url("AKIA/ID+1", "se/cret+key=")
        assert url == "sqs://AKIA%2FID%2B1:se%2Fcret%2Bkey%3D@"

    def test_should_omit_userinfo_without_credentials(self):
        assert broker_url(None, None) == "sqs://"

    def test_should_refuse_partial_credentials(self):
        with self.assertRaises(ValueError):
            broker_url("AKIA", None)
        with self.assertRaises(ValueError):
            broker_url(None, "secret")


class CeleryTasksTestCase(TestCase):
    def test_should_configure_broker_with_quoted_credentials(self):
        tasks = CeleryTasks("AKIA/ID", "se/cret", "us-east-1")
        assert tasks.celery.conf.broker_url == "sqs://AKIA%2FID:se%2Fcret@"
        assert (
            tasks.celery.conf.broker_transport_options["region"] == "us-east-1"
        )

    def test_should_not_set_time_limit_without_timeout(self):
        tasks = CeleryTasks(None, None, "us-east-1")
        assert tasks.celery.conf.broker_url == "sqs://"
        assert tasks.get_detect_task().time_limit is None

    def test_should_set_time_limit_from_timeout(self):
        tasks = CeleryTasks(None, None, "us-east-1", timeout=30)
        assert tasks.get_detect_task().time_limit == 30
        assert (
            tasks.celery.conf.broker_transport_options["visibility_timeout"]
            == 30
        )
