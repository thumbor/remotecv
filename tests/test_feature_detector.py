#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase

import numpy as np

from remotecv.detectors.feature_detector import FeatureDetector
from tests import create_16_bit_image, create_image, create_image_from_pixels


class FeatureDetectorTestCase(TestCase):
    def test_should_detect_multiple_points(self):
        detection_result = FeatureDetector().detect(
            create_image("no_face.jpg")
        )
        assert len(detection_result) > 4

    def test_should_run_on_images_with_mode_l(self):
        detection_result = FeatureDetector().detect(
            create_image("one_face-bw.png")
        )
        assert len(detection_result) > 4

    def test_should_run_on_jpeg_images_with_mode_l(self):
        detection_result = FeatureDetector().detect(
            create_image("multiple_faces_bw.jpg")
        )
        assert len(detection_result) > 4

    def test_should_run_on_images_with_mode_1(self):
        detection_result = FeatureDetector().detect(
            create_image("one_face-bw-1.png")
        )
        assert len(detection_result) > 4

    def test_should_run_on_16_bit_images(self):
        detection_result = FeatureDetector().detect(
            create_16_bit_image("one_face.jpg")
        )
        assert len(detection_result) > 4

    def test_should_run_on_16_bit_images_that_are_mostly_flat(self):
        pixels = np.zeros((400, 600), np.uint16)
        pixels[190:202, 290:302] = 4000
        detection_result = FeatureDetector().detect(
            create_image_from_pixels(pixels)
        )
        assert len(detection_result) == 4

    def test_should_not_detect_points(self):
        detection_result = FeatureDetector().detect(
            create_image("white-block.png")
        )
        assert not detection_result
