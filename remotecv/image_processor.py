
from remotecv.detectors.face_detector import FaceDetector
from remotecv.detectors.feature_detector import FeatureDetector
from remotecv.detectors.glasses_detector import GlassesDetector
from remotecv.detectors.profile_detector import ProfileDetector

class ImageProcessor:
    def __init__(self):
        self.detectors = {
            'face': FaceDetector(),
            'feat': FeatureDetector(),
            'glas': GlassesDetector(),
            'prof': ProfileDetector()
        }

    def detect(self, detector, size, mode, img_data):
        detector = self.detectors[detector]
        if detector is None:
            return None
        return detector.detect(size[0], size[1], mode, img_data)
