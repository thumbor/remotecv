#!/usr/bin/python
# -*- coding: utf-8 -*-

from remotecv.detectors.complete_detector import CompleteDetector
from remotecv.detectors.face_detector import FaceDetector
from remotecv.detectors.feature_detector import FeatureDetector
from remotecv.detectors.glasses_detector import GlassesDetector
from remotecv.detectors.profile_detector import ProfileDetector
from remotecv.image import Image


class ImageProcessor:
    def __init__(self):
        self.detectors = {
            "all": CompleteDetector(),
            "face": FaceDetector(),
            "feature": FeatureDetector(),
            "glass": GlassesDetector(),
            "profile": ProfileDetector(),
        }

    def detect(self, detector, image_data):
        result = []
        image = Image.create_from_buffer(image_data)
        if image is None:
            return []

        for detector_key in detector.split("+"):
            try:
                result = result + self.detectors[detector_key].detect(image)
            except KeyError as key_error:
                raise AttributeError("Detector unavailable") from key_error
        return result
