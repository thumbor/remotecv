from remotecv.result_store import BaseStore
from remotecv.utils import logger


class ResultStore(BaseStore):

    WEEK = 604800
    memcache_instance = None

    def __init__(self, config):
        super().__init__(config)

        # pylibmc must be imported
        import pylibmc  # pylint: disable=import-error,import-outside-toplevel

        if not ResultStore.memcache_instance:
            host_strings = config.memcache_hosts.split(",")
            ResultStore.memcache_instance = pylibmc.Client(
                host_strings,
                binary=True,
                behaviors={"tcp_nodelay": True, "no_block": True, "ketama": True},
            )
        self.storage = ResultStore.memcache_instance

    def store(self, key, points):
        result = self.serialize(points)
        logger.debug("Points found: %s", result)
        key = f"thumbor-detector-{key}"
        self.storage.set(key, result, time=2 * self.WEEK)
