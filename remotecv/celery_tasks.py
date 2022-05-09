from celery import Celery

from remotecv.pyres_tasks import DetectTask


class CeleryTasks:
    def __init__(self, key_id, key_secret, region, timeout=None, polling_interval=None):
        self.celery = Celery(broker=f"sqs://{key_id}:{key_secret}@")

        self.celery.conf.update(
            BROKER_TRANSPORT_OPTIONS={
                "region": region,
                "visibility_timeout": timeout or 120,
                "polling_interval": polling_interval or 20,
                "queue_name_prefix": "celery-remotecv-",
            }
        )

    def get_detect_task(self):
        @self.celery.task(ignore_result=True, acks_late=True)
        def detect_task(detection_type, image_path, key):
            DetectTask.perform(detection_type, image_path, key)

        return detect_task

    def run_commands(self, args, log_level=None):
        # We have to init the task so it can be found by the worker later
        self.get_detect_task()

        if log_level:
            self.celery.conf.update(CELERYD_LOG_LEVEL=log_level)
        self.celery.start(args)
