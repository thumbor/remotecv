#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.detectors.profile_detector import ProfileDetector
from remotecv.utils import context
from tests import create_image


class ProfileDetectorTestCase(TestCase):
    def setUp(self):
        context.metrics = mock.Mock()

    def test_should_detect_one_face(self):
        detection_result = ProfileDetector().detect(
            create_image("profile_face.jpg")
        )
        expect(detection_result).to_length(1)
        expect(detection_result[0][0]).to_be_numeric()
        expect(detection_result[0][1]).to_be_numeric()
        expect(detection_result[0][2]).to_be_numeric()
        expect(detection_result[0][3]).to_be_numeric()

    def test_should_not_detect(self):
        detection_result = ProfileDetector().detect(
            create_image("no_face.jpg")
        )
        expect(detection_result).to_length(0)
