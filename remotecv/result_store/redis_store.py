from redis import Redis

from remotecv.utils import logger
from remotecv.result_store import BaseStore

class ResultStore(BaseStore):

    WEEK = 604800
    redis_instance = None

    def __init__(self, config):
        if not ResultStore.redis_instance:
            ResultStore.redis_instance = Redis(host=config.redis_host, port=config.redis_port, db=config.redis_database, password=config.redis_password)
        self.storage = ResultStore.redis_instance

    def store(self, key, points):
        result = self.serialize(points)
        logger.debug("Points found: %s" % result)
        redis_key = "thumbor-detector-%s" % key
        self.storage.setex(redis_key, result, 2 * self.WEEK)
