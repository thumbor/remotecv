# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com <thumbor@g.globo>


from os.path import abspath, dirname, join

from remotecv.detectors import BaseDetector

import cv2
import numpy

HAIR_OFFSET = 0.12


class YuNetFaceDetector(BaseDetector):
    def __add_hair_offset(self, top, height):
        top = max(0, top - height * HAIR_OFFSET)
        return top

    def get_faces(self, image, image_size):
        model = cv2.FaceDetectorYN.create(
            model=join(
                abspath(dirname(__file__)), "face_detection_yunet_2022mar.onnx"
            ),
            config="",
            input_size=image_size,
            score_threshold=0.6,
            nms_threshold=0.3,
            top_k=5000,
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
            target_id=cv2.dnn.DNN_TARGET_CPU,
        )
        return model.detect(image)[1]

    def detect(self, image):
        features = self.get_faces(self.get_np_img(image), image.size)
        points = []
        if features.any():
            for face in features.astype(numpy.int32):
                left = face[0]
                top = face[1]
                width = face[2]
                height = face[3]
                top = self.__add_hair_offset(top, height)
                points.append([left, top, width, height])

        return points
