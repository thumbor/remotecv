# -*- coding: utf-8 -*-

import numbers
from unittest import TestCase

from remotecv.detectors.face_detector import FaceDetector
from tests import create_image


class FaceDetectorTestCase(TestCase):
    def test_should_detect_one_face(self):
        detection_result = FaceDetector().detect(create_image("one_face.jpg"))
        assert len(detection_result) == 1
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_detect_one_face_on_ico(self):
        detection_result = FaceDetector().detect(create_image("one_face.ico"))
        assert len(detection_result) == 1
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_not_detect(self):
        detection_result = FaceDetector().detect(create_image("no_face.jpg"))
        assert len(detection_result) == 0

    def test_should_not_detect_on_ico(self):
        detection_result = FaceDetector().detect(create_image("no_face.ico"))
        assert len(detection_result) == 0

    def test_should_run_on_multiple_faces(self):
        # Group Smile picture - Credit Richard Foster / Flickr Creative Commons
        detection_result = FaceDetector().detect(
            create_image("group-smile.jpg")
        )
        assert len(detection_result) > 4
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_run_on_grayscale_images(self):
        # Group Smile picture - Credit Richard Foster / Flickr Creative Commons
        detection_result = FaceDetector().detect(
            create_image("group-smile-bw.jpg")
        )
        assert len(detection_result) > 4
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_run_on_cmyk_images(self):
        detection_result = FaceDetector().detect(
            create_image("one_face_cmyk.jpg")
        )
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_run_on_images_with_alpha(self):
        detection_result = FaceDetector().detect(create_image("one_face.png"))
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_run_on_images_with_mode_l(self):
        detection_result = FaceDetector().detect(
            create_image("one_face-bw.png")
        )
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_run_on_images_with_mode_1(self):
        detection_result = FaceDetector().detect(
            create_image("one_face-bw-1.png")
        )
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)

    def test_should_run_on_images_with_mode_la(self):
        detection_result = FaceDetector().detect(
            create_image("one_face-bw-la.png")
        )
        assert isinstance(detection_result[0][0], numbers.Number)
        assert isinstance(detection_result[0][1], numbers.Number)
        assert isinstance(detection_result[0][2], numbers.Number)
        assert isinstance(detection_result[0][3], numbers.Number)
