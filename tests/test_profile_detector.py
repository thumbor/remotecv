#!/usr/bin/python
# -*- coding: utf-8 -*-

import numbers
from unittest import TestCase

from remotecv.detectors.profile_detector import ProfileDetector
from tests import create_image


class ProfileDetectorTestCase(TestCase):
    def test_should_detect_one_face(self):
        detection_result = ProfileDetector().detect(
            create_image("profile_face.jpg")
        )
        assert len(detection_result) == 1
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_not_detect(self):
        detection_result = ProfileDetector().detect(
            create_image("no_face.jpg")
        )
        assert len(detection_result) == 0
