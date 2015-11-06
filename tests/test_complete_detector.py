#!/usr/bin/python
# -*- coding: utf-8 -*-

from preggy import expect
from unittest import TestCase
from tests import create_image
from remotecv.detectors.complete_detector import CompleteDetector


class CompleteDetectorTestCase(TestCase):
    def test_should_detect_something(self):
        detection_result = CompleteDetector().detect(create_image('profile_face.jpg'))
        expect(detection_result).to_be_greater_than(20)
        expect(detection_result[0][0]).to_be_numeric()
        expect(detection_result[0][1]).to_be_numeric()
        expect(detection_result[0][2]).to_be_numeric()
        expect(detection_result[0][3]).to_be_numeric()
