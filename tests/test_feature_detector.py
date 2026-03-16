# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from remotecv.detectors.feature_detector import FeatureDetector
from tests import create_image


class FeatureDetectorTestCase(TestCase):
    def test_should_detect_multiple_points(self):
        detection_result = FeatureDetector().detect(
            create_image("no_face.jpg")
        )
        assert len(detection_result) > 4

    def test_should_not_detect_points(self):
        detection_result = FeatureDetector().detect(
            create_image("white-block.png")
        )
        assert not detection_result

    def test_should_return_none_when_corners_array_is_empty(self):
        import numpy as np  # pylint: disable=import-outside-toplevel

        with mock.patch("cv2.goodFeaturesToTrack") as gftt_mock:
            # Return an empty array (non-None but zero length)
            gftt_mock.return_value = np.array([]).reshape((0, 1, 2))
            detection_result = FeatureDetector().detect(
                create_image("no_face.jpg")
            )
        assert detection_result is None
