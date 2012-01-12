from remotecv.image_processor import ImageProcessor
from remotecv.result_store import ResultStore
from remotecv.utils import logger

class DetectTask:
    queue = "Detect"
    processor = ImageProcessor()

    @classmethod
    def to_key(clz, detection_type, image_path, crop_left, crop_top, crop_right, crop_bottom):
        key = "thumbor-detector-%s" % image_path
        if crop_left > 0 or crop_top > 0 or crop_right > 0 or crop_bottom > 0:
            key += '_%d_%d_%d_%d' % (crop_left, crop_top, crop_right, crop_bottom)
        return key

    @classmethod
    def perform(clz, detection_type, image_path, crop_left, crop_top, crop_right, crop_bottom):
        points = clz.processor.detect(detection_type, image_path, crop_left, crop_top, crop_right, crop_bottom)
        logger.debug("Points found: %s" % str(points))
        result_store = ResultStore()
        result_store.store(clz.to_key(detection_type, image_path, crop_left, crop_top, crop_right, crop_bottom), points)
