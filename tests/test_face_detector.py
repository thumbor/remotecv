#!/usr/bin/python
# -*- coding: utf-8 -*-

from preggy import expect
from unittest import TestCase
from tests import create_image
from remotecv.detectors.face_detector import FaceDetector


class FaceDetectorTestCase(TestCase):

    def test_should_detect_one_face(self):
        detection_result = FaceDetector().detect(create_image('one_face.jpg'))
        expect(detection_result).to_length(1)
        expect(detection_result[0][0]).to_be_numeric()
        expect(detection_result[0][1]).to_be_numeric()
        expect(detection_result[0][2]).to_be_numeric()
        expect(detection_result[0][3]).to_be_numeric()

    def test_should_not_detect(self):
        detection_result = FaceDetector().detect(create_image('no_face.jpg'))
        expect(detection_result).to_be_empty()

    def test_should_run_on_grayscale_images(self):
        detection_result = FaceDetector().detect(create_image('multiple_faces_bw.jpg'))
        expect(detection_result).to_be_greater_than(4)
        expect(detection_result[0][0]).to_be_numeric()
        expect(detection_result[0][1]).to_be_numeric()
        expect(detection_result[0][2]).to_be_numeric()
        expect(detection_result[0][3]).to_be_numeric()

    def test_should_run_on_cmyk_images(self):
        detection_result = FaceDetector().detect(create_image('one_face_cmyk.jpg'))
        expect(detection_result[0][0]).to_be_numeric()
        expect(detection_result[0][1]).to_be_numeric()
        expect(detection_result[0][2]).to_be_numeric()
        expect(detection_result[0][3]).to_be_numeric()

    def test_should_run_on_images_with_alpha(self):
        detection_result = FaceDetector().detect(create_image('one_face.png'))
        expect(detection_result[0][0]).to_be_numeric()
        expect(detection_result[0][1]).to_be_numeric()
        expect(detection_result[0][2]).to_be_numeric()
        expect(detection_result[0][3]).to_be_numeric()
