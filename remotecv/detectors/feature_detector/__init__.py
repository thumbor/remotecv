#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import cv2
import numpy as np

from remotecv.detectors import BaseDetector

# pylint: disable=no-member


class FeatureDetector(BaseDetector):
    def detect(self, image):
        img = self.get_np_img(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
        if corners is None:
            return None

        corners = np.int0(corners)

        if corners is not None and len(corners) > 0:
            points = []
            for corner in corners:  # pylint: disable=not-an-iterable
                left, top = corner.ravel()
                points.append([left, top, 1, 1])

            return points

        return None
