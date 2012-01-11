from remotecv.image_processor import ImageProcessor
from remotecv.utils import logger

class DetectTask:
    queue = "Detect"
    processor = ImageProcessor()

    @classmethod
    def perform(clz, detection_type, image_path):
        clz.processor.detect(detection_type, image_path)
