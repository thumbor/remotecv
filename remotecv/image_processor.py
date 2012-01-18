#!/usr/bin/python
# -*- coding: utf-8 -*-

from remotecv.detectors.face_detector import FaceDetector
from remotecv.detectors.feature_detector import FeatureDetector
from remotecv.detectors.glasses_detector import GlassesDetector
from remotecv.detectors.profile_detector import ProfileDetector
from remotecv.detectors.complete_detector import CompleteDetector
from remotecv.image import Image

class ImageProcessor:
    def __init__(self):
        self.detectors = {
            'all': CompleteDetector(),
            'face': FaceDetector(),
            'feat': FeatureDetector(),
            'glas': GlassesDetector(),
            'prof': ProfileDetector()
        }

    def detect(self, detector, image_data):
        detector = self.detectors[detector]
        if detector is None:
            return None

        image = Image.create_from_buffer(image_data)
        image.grayscale()
        return detector.detect(image)
