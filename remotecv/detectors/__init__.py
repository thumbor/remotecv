#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, dirname, abspath

import cv2
import numpy as np


class BaseDetector(object):
    def get_np_img(self, image):
        return np.array(image)

    def detect(self, context):
        raise NotImplementedError()


class CascadeLoaderDetector(BaseDetector):

    def load_cascade_file(self, module_path, cascade_file_path):
        cascade_file = join(abspath(dirname(module_path)), cascade_file_path)
        self.__class__.cascade = cv2.CascadeClassifier(cascade_file)

    def get_features(self, image):
        img = self.get_np_img(image)

        faces = self.__class__.cascade.detectMultiScale(
            img,
            1.7,
            1,
        )
        faces_scaled = []

        for (x, y, w, h) in faces:
            faces_scaled.append(((x, y, w, h), 0))

        return faces_scaled

    def detect(self, image):
        features = self.get_features(image)

        if features:
            points = [[left, top, width, height] for (left, top, width, height), neighbors in features]
        else:
            points = []

        return points
