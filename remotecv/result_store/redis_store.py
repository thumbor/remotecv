from remotecv.result_store import BaseStore
from remotecv.timing import get_time, get_interval
from remotecv.utils import context, logger, redis_client


class ResultStore(BaseStore):
    redis_instance = None

    def __init__(self, config):
        super().__init__(config)
        if not ResultStore.redis_instance:
            ResultStore.redis_instance = redis_client()

        self.redis_key_expire_time = config.redis_key_expire_time
        self.storage = ResultStore.redis_instance

    def store(self, key, points):
        start_time = get_time()
        result = self.serialize(points)
        logger.debug("Points found: %s", result)
        redis_key = f"thumbor-detector-{key}"
        self.storage.set(
            name=redis_key,
            value=result,
            ex=self.redis_key_expire_time,
        )
        context.metrics.timing(
            "worker.store_points.time",
            get_interval(start_time, get_time()),
        )
