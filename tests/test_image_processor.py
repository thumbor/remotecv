from unittest import TestCase
from preggy import expect
from tests import read_fixture
from nose.tools import raises

from remotecv.image_processor import ImageProcessor


class ImageProcessorTest(TestCase):

    @raises(AttributeError)
    def test_when_detector_unavailable(self):
        image_processor = ImageProcessor()
        image_processor.detect('feat', read_fixture('broken.jpg'))

    def test_when_image_is_huge(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect('all', read_fixture('huge_image.jpg'))
        expect(detect).Not.to_be_empty()

    def test_with_multiple_detectors(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect(
            'face+profile+glass',
            read_fixture('one_face.gif')
        )
        expect(detect).Not.to_be_empty()

    def test_when_not_animated_gif(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect('face', read_fixture('one_face.gif'))
        expect(detect).Not.to_be_empty()

    def test_when_animated_gif(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect('all', read_fixture('animated.gif'))
        expect(detect).to_be_empty()

    def test_feature_detection(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect('feature', read_fixture('broken.jpg'))
        expect(detect).Not.to_be_empty()

    def test_should_be_empty_when_invalid_image(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect('all', 'asdas')
        expect(detect).to_be_empty()

    def test_should_ignore_gif(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect('all', 'asdas')
        expect(detect).to_be_empty()
