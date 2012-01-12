#!/usr/bin/python
# -*- coding: utf-8 -*-

from remotecv.detectors.face_detector import FaceDetector
from remotecv.detectors.feature_detector import FeatureDetector
from remotecv.detectors.glasses_detector import GlassesDetector
from remotecv.detectors.profile_detector import ProfileDetector
from remotecv.detectors.complete_detector import CompleteDetector
from remotecv.loader import load
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

    def detect(self, detector, image_path, crop_left, crop_top, crop_right, crop_bottom):
        detector = self.detectors[detector]
        if detector is None:
            return None

        image_buffer = load(image_path)
        image = Image(image_buffer)
        image.grayscale()
        image.crop(crop_left, crop_top, crop_right, crop_bottom)
        return detector.detect(image)
