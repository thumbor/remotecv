from unittest import TestCase
from preggy import expect
from . import read_fixture
from nose.tools import raises

from remotecv.image_processor import ImageProcessor


class ImageProcessorTest(TestCase):

    @raises(AttributeError)
    def test_when_detector_unavailable(self):
        image_processor = ImageProcessor()
        image_processor.detect('feat', read_fixture('broken.jpg'))

    def test_when_detector_available(self):
        image_processor = ImageProcessor()
        for detector in ['all', 'face', 'feature', 'glass', 'profile']:
            detect = image_processor.detect(detector, read_fixture('broken.jpg'))
            expect(detect).Not.to_be_empty()

    def test_when_image_is_huge(self):
        image_processor = ImageProcessor()
        detect = image_processor.detect('face', read_fixture('huge_image.jpg'))
        expect(detect).Not.to_be_empty()
