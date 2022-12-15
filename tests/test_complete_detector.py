#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.detectors.complete_detector import CompleteDetector
from remotecv.utils import context
from tests import create_image


class CompleteDetectorTestCase(TestCase):
    def test_should_detect_something(self):
        context.metrics = mock.Mock()
        detection_result = CompleteDetector().detect(create_image("profile_face.jpg"))
        expect(len(detection_result)).to_be_greater_than(20)
        expect(detection_result[0][0]).to_be_numeric()
        expect(detection_result[0][1]).to_be_numeric()
        expect(detection_result[0][2]).to_be_numeric()
        expect(detection_result[0][3]).to_be_numeric()
