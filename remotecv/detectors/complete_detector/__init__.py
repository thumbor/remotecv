#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from remotecv.detectors import CascadeLoaderDetector
from remotecv.detectors.face_detector import FaceDetector
from remotecv.detectors.feature_detector import FeatureDetector
from remotecv.detectors.glasses_detector import GlassesDetector
from remotecv.detectors.profile_detector import ProfileDetector


class CompleteDetector(CascadeLoaderDetector):
    def detect(self, image):
        face_detector = FaceDetector()
        glasses_detector = GlassesDetector()
        profile_detector = ProfileDetector()
        feature_detector = FeatureDetector()

        face_points = face_detector.detect(image) or []
        glasses_points = glasses_detector.detect(image) or []
        profile_points = profile_detector.detect(image) or []
        feature_points = feature_detector.detect(image) or []

        return face_points + glasses_points + profile_points + feature_points
