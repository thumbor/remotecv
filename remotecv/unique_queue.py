from pyres import ResQ
from pyres.worker import Worker

from remotecv.utils import logger


class UniqueQueue(ResQ):
    def _escape_for_key(self, value):
        return value.replace(" ", "").replace("\n", "")

    def _create_unique_key(self, queue, key):
        return f"resque:unique:queue:{queue}%s:{self._escape_for_key(str(key))}%s"

    def add_unique_key(self, queue, key):
        unique_key = self._create_unique_key(queue, key)
        if self.redis.get(unique_key) == "1":
            # Do nothing as this message is already enqueued
            return False

        self.redis.set(unique_key, "1")
        return True

    def del_unique_key(self, queue, key):
        unique_key = self._create_unique_key(queue, key)
        self.redis.delete(unique_key)

    def enqueue_unique_from_string(self, klass_as_string, queue, args=None, key=None):
        if not self.add_unique_key(queue, key):
            logger.debug("key %s already enqueued", key)
            return

        if not args:
            args = []

        payload = {
            "class": klass_as_string,
            "queue": queue,
            "args": args + [key],
            "key": key,
        }
        self.push(queue, payload)
        logger.info("enqueued '%s' job on queue %s", klass_as_string, queue)
        if args:
            logger.debug("job arguments: %s", str(args))
        else:
            logger.debug("no arguments passed in.")


class UniqueWorker(Worker):
    def __init__(
        self,
        queues=(),
        server="localhost:6379",
        password=None,
        timeout=None,
        after_fork=None,
    ):
        self.after_fork_fn = after_fork
        super().__init__(
            queues, UniqueQueue(server=server), password, timeout
        )

    def after_fork(self, job):
        if self.after_fork_fn and callable(self.after_fork_fn):
            self.after_fork_fn(job)

    def before_process(self, job):
        self.resq.del_unique_key(
            job._queue, job._payload["key"]  # pylint: disable=protected-access
        )
        return job
