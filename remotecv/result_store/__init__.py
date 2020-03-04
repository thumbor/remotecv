import json


class BaseStore:
    def __init__(self, config):
        self.config = config

    def serialize(self, points):
        result_array = []
        for point in points:
            result = {
                "x": point[0] + (int(point[2]) / 2),
                "y": point[1] + (int(point[3]) / 2),
                "height": int(point[2]),
                "width": int(point[3]),
                "origin": "",
            }
            result["z"] = result["width"] * result["height"]
            result_array.append(result)

        return json.dumps(result_array)

    def store(self, key, points):
        raise NotImplementedError()
