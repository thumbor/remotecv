# -*- coding: utf-8 -*-

import numbers
from unittest import TestCase

from remotecv.detectors.complete_detector import CompleteDetector
from tests import create_image


class CompleteDetectorTestCase(TestCase):
    def test_should_detect_something(self):
        detection_result = CompleteDetector().detect(
            create_image("profile_face.jpg")
        )
        assert len(detection_result) > 20
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)
