#!/usr/bin/python
# -*- coding: utf-8 -*-

import numbers
from unittest import TestCase

from remotecv.detectors.complete_detector import CompleteDetector
from tests import create_16_bit_image, create_image, create_image_as


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

    def test_should_run_on_images_with_mode_l(self):
        detection_result = CompleteDetector().detect(
            create_image("one_face-bw.png")
        )
        assert len(detection_result) > 20

    def test_should_run_on_16_bit_images(self):
        detection_result = CompleteDetector().detect(
            create_16_bit_image("one_face.jpg")
        )
        assert len(detection_result) > 20

    def test_should_not_detect_on_images_opencv_cannot_decode(self):
        detection_result = CompleteDetector().detect(
            create_image_as("one_face.jpg", "PCX")
        )
        assert not detection_result
