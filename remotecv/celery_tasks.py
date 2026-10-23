from urllib.parse import quote

from celery import Celery
from redis import RedisError

from remotecv.tasks import DetectTask
from remotecv.timing import get_interval, get_time
from remotecv.utils import context, logger, redact_url

DETECT_QUEUE = "detect"
UNIQUE_KEY_EXPIRE_TIME = 1209600


def build_sqs_broker(
    key_id, key_secret, region, visibility_timeout=None, polling_interval=None
):
    transport_options = {
        "region": region,
        "visibility_timeout": visibility_timeout or 120,
        "polling_interval": polling_interval or 20,
        "queue_name_prefix": "celery-remotecv-",
    }
    if not key_id and not key_secret:
        return "sqs://", transport_options
    if not key_id or not key_secret:
        raise ValueError("AWS key id and secret must be set together")
    auth = f"{quote(key_id, safe='')}:{quote(key_secret, safe='')}"
    return f"sqs://{auth}@", transport_options


class CeleryUniqueQueue:
    def __init__(self, redis, expire_time=UNIQUE_KEY_EXPIRE_TIME):
        self.redis = redis
        self.expire_time = expire_time

    def _escape_for_key(self, value):
        return value.replace(" ", "").replace("\n", "")

    def _create_unique_key(self, queue, key):
        return f"celery:unique:queue:{queue}:{self._escape_for_key(str(key))}"

    def add_unique_key(self, queue, key):
        unique_key = self._create_unique_key(queue, key)
        # Use an atomic SET with NX to avoid race conditions between producers.
        # redis-py returns True if the key was set, and None if it already existed.
        added = self.redis.set(
            unique_key,
            "1",
            ex=self.expire_time,
            nx=True,
        )
        return bool(added)

    def del_unique_key(self, queue, key):
        self.redis.delete(self._create_unique_key(queue, key))


def _release_unique_key(unique_queue, key):
    start_time = get_time()
    try:
        unique_queue.del_unique_key(DETECT_QUEUE, key)
    except RedisError as error:
        logger.warning(
            "could not release unique key %s: %s", redact_url(str(key)), error
        )
        return
    context.metrics.timing(
        "worker.del_unique_key.time",
        get_interval(start_time, get_time()),
    )


class CeleryTasks:
    def __init__(
        self,
        broker_url,
        broker_transport_options=None,
        unique_queue=None,
        time_limit=None,
    ):
        self.celery = Celery(broker=broker_url)

        if broker_transport_options:
            self.celery.conf.update(
                BROKER_TRANSPORT_OPTIONS=broker_transport_options
            )
        self.unique_queue = unique_queue
        self.time_limit = time_limit
        self._detect_task = None

    def get_detect_task(self):
        if self._detect_task is not None:
            return self._detect_task

        unique_queue = self.unique_queue

        @self.celery.task(
            ignore_result=True, acks_late=True, time_limit=self.time_limit
        )
        def detect_task(detection_type, image_path, key):
            if unique_queue is not None:
                _release_unique_key(unique_queue, key)
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
            logger.debug("key %s already enqueued", redact_url(str(key)))
            return
        try:
            self.get_detect_task().apply_async(
                args=[detection_type, image_path, key]
            )
        except Exception:
            self.unique_queue.del_unique_key(DETECT_QUEUE, key)
            raise
        logger.info("enqueued detect task for key %s", redact_url(str(key)))

    def run_commands(self, args, log_level=None):
        # We have to init the task so it can be found by the worker later
        self.get_detect_task()

        if log_level:
            self.celery.conf.update(CELERYD_LOG_LEVEL=log_level)
        self.celery.start(args)
