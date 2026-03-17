from celery import Celery

from remotecv.tasks import DetectTask
from remotecv.timing import get_interval, get_time
from remotecv.utils import config, context, logger, redis_client

DETECT_QUEUE = "detect"


class CeleryUniqueQueue:
    def __init__(self, redis):
        self.redis = redis

    def _escape_for_key(self, value):
        return value.replace(" ", "").replace("\n", "")

    def _create_unique_key(self, queue, key):
        return f"celery:unique:queue:{queue}:{self._escape_for_key(str(key))}"

    def add_unique_key(self, queue, key):
        unique_key = self._create_unique_key(queue, key)
        if self.redis.get(unique_key) == b"1":
            # Do nothing as this message is already enqueued
            return False
        self.redis.set(unique_key, "1", ex=config.redis_key_expire_time)
        return True

    def del_unique_key(self, queue, key):
        start_time = get_time()
        unique_key = self._create_unique_key(queue, key)
        self.redis.delete(unique_key)
        context.metrics.timing(
            "worker.del_unique_key.time",
            get_interval(start_time, get_time()),
        )


class CeleryTasks:
    def __init__(
        self,
        key_id,
        key_secret,
        region,
        timeout=None,
        polling_interval=None,
    ):  # pylint: disable=too-many-positional-arguments
        self.celery = Celery(broker=f"sqs://{key_id}:{key_secret}@")

        self.celery.conf.update(
            BROKER_TRANSPORT_OPTIONS={
                "region": region,
                "visibility_timeout": timeout or 120,
                "polling_interval": polling_interval or 20,
                "queue_name_prefix": "celery-remotecv-",
            }
        )
        self.unique_queue = CeleryUniqueQueue(redis_client())
        self._detect_task = None

    def get_detect_task(self):
        if self._detect_task is not None:
            return self._detect_task

        unique_queue = self.unique_queue

        @self.celery.task(ignore_result=True, acks_late=True)
        def detect_task(detection_type, image_path, key):
            unique_queue.del_unique_key(DETECT_QUEUE, key)
            start_time = get_time()
            DetectTask.perform(detection_type, image_path, key)

            context.metrics.timing(
                "worker.celery_task.time",
                get_interval(start_time, get_time()),
            )
            context.metrics.incr("worker.celery_task.total")

        self._detect_task = detect_task
        return detect_task

    def enqueue_unique(self, detection_type, image_path, key):
        if not self.unique_queue.add_unique_key(DETECT_QUEUE, key):
            logger.debug("key %s already enqueued", key)
            return
        self.get_detect_task().apply_async(
            args=[detection_type, image_path, key]
        )
        logger.info("enqueued detect task for key %s", key)

    def run_commands(self, args, log_level=None):
        # We have to init the task so it can be found by the worker later
        self.get_detect_task()

        if log_level:
            self.celery.conf.update(CELERYD_LOG_LEVEL=log_level)
        self.celery.start(args)
