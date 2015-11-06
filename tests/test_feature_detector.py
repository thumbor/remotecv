#!/usr/bin/python
# -*- coding: utf-8 -*-

from preggy import expect
from unittest import TestCase
from tests import create_image

from remotecv.detectors.feature_detector import FeatureDetector


class FeatureDetectorTestCase(TestCase):
    def test_should_detect_multiple_points(self):
        detection_result = FeatureDetector().detect(create_image('no_face.jpg'))
        expect(detection_result).to_be_greater_than(4)

    def test_should_not_detect_points(self):
        detection_result = FeatureDetector().detect(create_image('white-block.png'))
        expect(detection_result).to_be_false()
