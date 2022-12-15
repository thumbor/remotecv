from unittest import TestCase, mock

from preggy import expect

from remotecv.image_processor import ImageProcessor
from remotecv.utils import context
from tests import read_fixture


class ImageProcessorTest(TestCase):
    def setUp(self):
        context.metrics = mock.Mock()

    def test_when_detector_unavailable(self):
        image_processor = ImageProcessor()
        with expect.error_to_happen(AttributeError):
            image_processor.detect("feat", read_fixture("broken.jpg"))

    def test_when_image_is_huge(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect("all", read_fixture("huge_image.jpg"))
        expect(detect).Not.to_be_empty()

    def test_with_multiple_detectors(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect(
            "face+profile+glass", read_fixture("one_face.jpg")
        )
        expect(detect).Not.to_be_empty()

    def test_when_not_animated_gif(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect("face", read_fixture("one_face.gif"))
        expect(detect).Not.to_be_empty()

    def test_when_animated_gif(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect("all", read_fixture("animated.gif"))
        expect(detect).to_be_empty()

    def test_feature_detection(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect(
            "feature", read_fixture("one_face.jpg")
        )
        expect(detect).Not.to_be_empty()

    def test_should_be_empty_when_invalid_image(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect("all", b"asdas")
        expect(detect).to_be_empty()

    def test_should_ignore_gif(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect("all", b"asdas")
        expect(detect).to_be_empty()
