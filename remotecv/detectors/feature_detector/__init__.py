#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import cv

from remotecv.detectors import BaseDetector

class FeatureDetector(BaseDetector):

    def detect(self, image):
        rows, cols = image.size

        eig_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        temp_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        points = cv.GoodFeaturesToTrack(image.image, eig_image, temp_image, 20, 0.04, 1.0, useHarris = False)

        if points:
            return [[x, y, 1, 1] for x, y in points]

        return None
