from tests import create_image
from remotecv.detectors.yunet_face_detector import YuNetFaceDetector
from remotecv.detectors.face_detector import FaceDetector


image = create_image("group-smile.jpg")


def face_detection():
    FaceDetector().detect(image)


def yunet_face_detection():
    YuNetFaceDetector().detect(image)


__benchmarks__ = [
    (
        face_detection,
        yunet_face_detection,
        "Current detector Vs. YuNet Face Detector",
    )
]
