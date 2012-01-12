from pyres import ResQ
from pyres.worker import Worker

class UniqueQueue(ResQ):
    def _escape_for_key(self, value):
        return value.replace(" ", "").replace("\n", "")

    def _create_unique_key(self, queue, args):
        key = "_".join([str(arg) for arg in args])
        return "resque:unique:queue:%s:%s" % (queue, self._escape_for_key(str(key)))

    def add_unique_key(self, queue, args):
        unique_key = self._create_unique_key(queue, args)
        if self.redis.get(unique_key) == "1":
            # Do nothing as this message is already enqueued
            return False

        self.redis.set(unique_key, "1")
        return True

    def del_unique_key(self, queue, args):
        unique_key = self._create_unique_key(queue, args)
        self.redis.delete(unique_key)

    def push(self, queue, item):
        if not self.add_unique_key(queue, item['args']):
            return

        super(UniqueQueue, self).push(queue, item)


class UniqueWorker(Worker):

    def __init__(self, queues=None, server="localhost:6379", password=None):
        if not queues:
            queues = ()
        super(UniqueWorker, self).__init__(queues, UniqueQueue(server=server), password)

    def before_process(self, job):
        self.resq.del_unique_key(job._queue, job._payload['args'])
        return job
