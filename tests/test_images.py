from unittest import TestCase
from preggy import expect
from tests import create_image


class ImageTest(TestCase):

    def test_should_read_a_psd(self):
        im = create_image('why_not_a.psd')
        expect(im).Not.to_be_null()
        expect(im.size).to_equal((620, 413))

    def test_when_image_is_broken(self):
        im = create_image('broken.jpg')
        expect(im).Not.to_be_null()
        expect(im.size).to_equal((600, 769))

    def test_when_image_is_pallete(self):
        im = create_image('pallete.png')
        expect(im).Not.to_be_null()
        expect(im.size).to_equal((3317, 2083))
