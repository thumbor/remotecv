#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import cv2

from remotecv.detectors import BaseDetector


class FeatureDetector(BaseDetector):
    def detect(self, image):
        points = cv2.goodFeaturesToTrack(
            self.get_np_img(image),
            maxCorners=20,
            qualityLevel=0.04,
            minDistance=1.0,
            useHarrisDetector=False,
        )

        if points is not None and len(points) > 0:
            return [[point[0][0].item(), point[0][1].item(), 1, 1] for point in points]

        return None
