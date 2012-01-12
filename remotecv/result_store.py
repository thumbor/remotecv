import json

import redis

from remotecv.utils import config

class ResultStore:

    def __init__(self):
        self.storage = redis.Redis(port=config.redis_port,
                                   host=config.redis_host)

    def to_dict(self, points):
        result = {
            'x': points[0] + (int(points[2]) / 2),
            'y': points[1] + (int(points[3]) / 2),
            'height': int(points[2]),
            'width': int(points[3]),
            'origin': ''
        }
        result['z'] = result['width'] * result['height']
        return result

    def store(self, key, points):
        self.storage.set(key, json.dumps([self.to_dict(point) for point in points]))
