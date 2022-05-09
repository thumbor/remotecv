from remotecv.result_store import BaseStore
from remotecv.utils import logger, redis_client


class ResultStore(BaseStore):

    WEEK = 604800
    redis_instance = None

    def __init__(self, config):
        super().__init__(config)

        if not ResultStore.redis_instance:
            ResultStore.redis_instance = redis_client()
        self.storage = ResultStore.redis_instance

    def store(self, key, points):
        result = self.serialize(points)
        logger.debug("Points found: %s", result)
        redis_key = f"thumbor-detector-{key}"
        self.storage.setex(
            name=redis_key,
            value=result,
            time=2 * self.WEEK,
        )
