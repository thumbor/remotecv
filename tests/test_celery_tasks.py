from unittest import TestCase

from preggy import expect

from remotecv.celery_tasks import CeleryTasks, broker_url


class BrokerUrlTestCase(TestCase):
    def test_should_quote_credentials(self):
        url = broker_url("AKIA/ID+1", "se/cret+key=")
        expect(url).to_equal("sqs://AKIA%2FID%2B1:se%2Fcret%2Bkey%3D@")

    def test_should_omit_userinfo_without_credentials(self):
        expect(broker_url(None, None)).to_equal("sqs://")

    def test_should_refuse_partial_credentials(self):
        with expect.error_to_happen(ValueError):
            broker_url("AKIA", None)
        with expect.error_to_happen(ValueError):
            broker_url(None, "secret")


class CeleryTasksTestCase(TestCase):
    def test_should_configure_broker_with_quoted_credentials(self):
        tasks = CeleryTasks("AKIA/ID", "se/cret", "us-east-1")
        expect(tasks.celery.conf.broker_url).to_equal(
            "sqs://AKIA%2FID:se%2Fcret@"
        )
        expect(tasks.celery.conf.broker_transport_options["region"]).to_equal(
            "us-east-1"
        )

    def test_should_not_set_time_limit_without_timeout(self):
        tasks = CeleryTasks(None, None, "us-east-1")
        expect(tasks.celery.conf.broker_url).to_equal("sqs://")
        expect(tasks.get_detect_task().time_limit).to_be_null()

    def test_should_set_time_limit_from_timeout(self):
        tasks = CeleryTasks(None, None, "us-east-1", timeout=30)
        expect(tasks.get_detect_task().time_limit).to_equal(30)
        expect(
            tasks.celery.conf.broker_transport_options["visibility_timeout"]
        ).to_equal(30)
