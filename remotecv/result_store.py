import json

from remotecv.utils import logger

class ResultStore:

    def __init__(self, redis):
        self.storage = redis

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
        points_map = [self.to_dict(point) for point in points]
        logger.debug("Points found: %s" % str(points_map))
        self.storage.set("thumbor-detector-%s" % key, json.dumps(points_map))
