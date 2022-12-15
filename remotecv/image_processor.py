#!/usr/bin/python
# -*- coding: utf-8 -*-

from remotecv.detectors.complete_detector import CompleteDetector
from remotecv.detectors.face_detector import FaceDetector
from remotecv.detectors.feature_detector import FeatureDetector
from remotecv.detectors.glasses_detector import GlassesDetector
from remotecv.detectors.profile_detector import ProfileDetector
from remotecv.image import Image
from remotecv.timing import get_time, get_interval
from remotecv.utils import context


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
        image = Image.create_from_buffer(image_data)
        if image is None:
            return []

        return self.run_detections(image, detector.split("+"))

    def run_detections(self, image, detectors):
        result = []
        for detector in detectors:
            try:
                start_time = get_time()
                points = self.detectors[detector].detect(image)
                context.metrics.timing(
                    f"worker.{detector}.time",
                    get_interval(start_time, get_time()),
                )
                if points:
                    context.metrics.incr(f"worker.{detector}.detected")

                result = result + points
            except KeyError as key_error:
                raise AttributeError("Detector unavailable") from key_error

        return result
