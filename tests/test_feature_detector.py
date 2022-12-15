#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.detectors.feature_detector import FeatureDetector
from remotecv.utils import context
from tests import create_image


class FeatureDetectorTestCase(TestCase):
    def setUp(self):
        context.metrics = mock.Mock()

    def test_should_detect_multiple_points(self):
        detection_result = FeatureDetector().detect(
            create_image("no_face.jpg")
        )
        expect(len(detection_result)).to_be_greater_than(4)

    def test_should_not_detect_points(self):
        detection_result = FeatureDetector().detect(
            create_image("white-block.png")
        )
        expect(detection_result).to_be_false()
