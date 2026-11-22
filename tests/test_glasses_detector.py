#!/usr/bin/python
# -*- coding: utf-8 -*-

import numbers
from unittest import TestCase

import numpy as np

from remotecv.detectors.glasses_detector import GlassesDetector
from tests import (
    create_16_bit_image,
    create_image,
    create_image_from_pixels,
    read_gray_pixels,
)


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

    def test_should_run_on_16_bit_images(self):
        detection_result = GlassesDetector().detect(
            create_16_bit_image("glasses.jpg")
        )
        assert len(detection_result) == 2

    def test_should_run_on_16_bit_images_using_part_of_the_range(self):
        detection_result = GlassesDetector().detect(
            create_16_bit_image("glasses.jpg", used_bits=12)
        )
        assert len(detection_result) == 2

    def test_should_run_on_16_bit_images_with_a_stuck_pixel(self):
        pixels = read_gray_pixels("glasses.jpg").astype(np.uint16) << 4
        pixels[0, 0] = 65535
        detection_result = GlassesDetector().detect(
            create_image_from_pixels(pixels)
        )
        assert len(detection_result) == 2

    def test_should_run_on_float_images(self):
        pixels = read_gray_pixels("glasses.jpg").astype(np.float32) / 255
        detection_result = GlassesDetector().detect(
            create_image_from_pixels(pixels, "TIFF")
        )
        assert len(detection_result) == 2

    def test_should_reject_images_with_non_finite_pixels(self):
        pixels = read_gray_pixels("glasses.jpg").astype(np.float32) / 255
        pixels[0, 0] = np.inf
        with self.assertRaises(ValueError):
            GlassesDetector().detect(create_image_from_pixels(pixels, "TIFF"))
