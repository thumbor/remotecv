from celery import Celery
from kombu.utils.url import safequote

from remotecv.pyres_tasks import DetectTask
from remotecv.timing import get_interval, get_time
from remotecv.utils import context


def broker_url(key_id, key_secret):
    if not key_id and not key_secret:
        return "sqs://"
    if not key_id or not key_secret:
        raise ValueError("AWS key id and key secret must be set together")
    return f"sqs://{safequote(key_id)}:{safequote(key_secret)}@"


class CeleryTasks:
    def __init__(
        self,
        key_id,
        key_secret,
        region,
        timeout=None,
        polling_interval=None,
    ):  # pylint: disable=too-many-positional-arguments
        self.timeout = timeout
        self.celery = Celery(broker=broker_url(key_id, key_secret))

        self.celery.conf.update(
            BROKER_TRANSPORT_OPTIONS={
                "region": region,
                "visibility_timeout": timeout or 120,
                "polling_interval": polling_interval or 20,
                "queue_name_prefix": "celery-remotecv-",
            }
        )

    def get_detect_task(self):
        @self.celery.task(
            ignore_result=True, acks_late=True, time_limit=self.timeout
        )
        def detect_task(detection_type, image_path, key):
            start_time = get_time()
            DetectTask.perform(detection_type, image_path, key)

            context.metrics.timing(
                "worker.celery_task.time",
                get_interval(start_time, get_time()),
            )
            context.metrics.incr("worker.celery_task.total")

        return detect_task

    def run_commands(self, args, log_level=None):
        # We have to init the task so it can be found by the worker later
        self.get_detect_task()

        if log_level:
            self.celery.conf.update(CELERYD_LOG_LEVEL=log_level)
        self.celery.start(args)
