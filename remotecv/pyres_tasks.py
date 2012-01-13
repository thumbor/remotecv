from remotecv.image_processor import ImageProcessor
from remotecv.result_store import ResultStore

class DetectTask:
    queue = "Detect"
    processor = ImageProcessor()

    @classmethod
    def perform(clz, detection_type, image_path, key):
        points = clz.processor.detect(detection_type, image_path)
        result_store = ResultStore()
        result_store.store(key, points)
