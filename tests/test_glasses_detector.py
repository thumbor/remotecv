# -*- coding: utf-8 -*-

import numbers
from unittest import TestCase

from remotecv.detectors.glasses_detector import GlassesDetector
from tests import create_image


class GlassesDetectorTestCase(TestCase):
    def test_should_detect_glasses(self):
        detection_result = GlassesDetector().detect(
            create_image("glasses.jpg")
        )
        assert len(detection_result) == 2
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)
        assert isinstance(detection_result[1][0], numbers.Number)
        assert isinstance(detection_result[1][1], numbers.Number)
        assert isinstance(detection_result[1][2], numbers.Number)
        assert isinstance(detection_result[1][3], numbers.Number)
