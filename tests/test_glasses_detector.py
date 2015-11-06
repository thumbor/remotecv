#!/usr/bin/python
# -*- coding: utf-8 -*-

from preggy import expect
from unittest import TestCase
from tests import create_image

from remotecv.detectors.glasses_detector import GlassesDetector


class GlassesDetectorTestCase(TestCase):
    def test_should_detect_glasses(self):
        detection_result = GlassesDetector().detect(create_image('glasses.jpg'))
        expect(detection_result).to_length(2)
        expect(detection_result[0][0]).to_be_numeric()
        expect(detection_result[0][1]).to_be_numeric()
        expect(detection_result[0][2]).to_be_numeric()
        expect(detection_result[0][3]).to_be_numeric()
        expect(detection_result[1][0]).to_be_numeric()
        expect(detection_result[1][1]).to_be_numeric()
        expect(detection_result[1][2]).to_be_numeric()
        expect(detection_result[1][3]).to_be_numeric()
