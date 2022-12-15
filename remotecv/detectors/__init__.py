#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from io import BytesIO
from os.path import abspath, dirname, join

import cv2
import numpy as np


class BaseDetector:
    def __get_format(self, image):
        fmt = image.format
        if fmt == "GIF":
            return "PNG"
        return fmt

    def get_np_img(self, image):
        img_buffer = BytesIO()
        image.save(img_buffer, self.__get_format(image))
        results = img_buffer.getvalue()
        img_buffer.close()
        nparr = np.frombuffer(results, np.uint8)
        return cv2.imdecode(
            nparr, cv2.IMREAD_UNCHANGED
        )  # pylint: disable=no-member

    def detect(self, image):
        raise NotImplementedError()


class CascadeLoaderDetector(BaseDetector):
    def load_cascade_file(self, module_path, cascade_file_path):
        cascade_file = join(abspath(dirname(module_path)), cascade_file_path)
        self.__class__.cascade = cv2.CascadeClassifier(
            cascade_file
        )  # pylint: disable=no-member

    def get_min_size_for(self, size):
        ratio = int(min(size[0], size[1]) / 15)
        ratio = max(20, ratio)
        return (ratio, ratio)

    def get_features(self, image):
        img = self.get_np_img(image)

        return self.get_faces(img, image.size)

    def get_grayscale_equalized_features(self, image):
        img = self.get_np_img(image)
        img_equalized = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

        return self.get_faces(img_equalized, image.size)

    def get_faces(self, image, image_size):
        faces = self.__class__.cascade.detectMultiScale(
            image, 1.2, 4, minSize=self.get_min_size_for(image_size)
        )
        faces_scaled = []

        for (left, top, width, height) in faces:
            faces_scaled.append(
                ((left.item(), top.item(), width.item(), height.item()), 0)
            )

        return faces_scaled

    def detect(self, image):
        features = self.get_features(image)

        if features:
            points = [
                [left, top, width, height]
                for (left, top, width, height), neighbors in features
            ]
        else:
            points = []

        return points
