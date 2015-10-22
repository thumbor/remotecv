from unittest import TestCase
from preggy import expect
from . import read_fixture

from remotecv.image import Image


class ImageTest(TestCase):

    def test_should_read_a_psd(self):
        im = Image.create_from_buffer(read_fixture('why_not_a.psd'))
        expect(im.image).Not.to_be_null()
        expect(im.size).to_equal((620, 413))

    def test_when_image_is_broken(self):
        im = Image.create_from_buffer(read_fixture('broken.jpg'))
        expect(im.image).Not.to_be_null()
        expect(im.size).to_equal((600, 769))
