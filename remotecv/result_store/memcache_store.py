import pylibmc

from remotecv.utils import logger
from remotecv.result_store import BaseStore

class ResultStore(BaseStore):

    WEEK = 604800
    memcache_instance = None

    def __init__(self, config):
        if not ResultStore.memcache_instance:
            host_strings = config.memcache_hosts.split(',')
            ResultStore.memcache_instance = pylibmc.Client(
                host_strings,
                binary=True,
                behaviors={
                    "tcp_nodelay": True,
                    'no_block': True,
                    "ketama": True
                }
            )
        self.storage = ResultStore.memcache_instance

    def store(self, key, points):
        result = self.serialize(points)
        logger.debug("Points found: %s" % result)
        key = "thumbor-detector-%s" % key
        self.storage.set(key, result, time=2*self.WEEK)
