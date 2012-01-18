from remotecv.image_processor import ImageProcessor
from remotecv.result_store import ResultStore
from remotecv.utils import config

class DetectTask:
    queue = "Detect"
    processor = ImageProcessor()

    @classmethod
    def perform(clz, detection_type, image_path, key):
        image_data = config.loader.load_sync(image_path)
        points = clz.processor.detect(detection_type, image_data)
        result_store = ResultStore()
        result_store.store(key, points)
