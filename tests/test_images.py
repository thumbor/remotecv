from unittest import TestCase

from preggy import expect

from tests import create_image


class ImageTest(TestCase):
    def test_should_read_a_psd(self):
        image = create_image("why_not_a.psd")
        expect(image).Not.to_be_null()
        expect(image.size).to_equal((620, 413))

    def test_when_image_is_broken(self):
        image = create_image("broken.jpg")
        expect(image).Not.to_be_null()
        expect(image.size).to_equal((600, 769))

    def test_when_image_is_pallete(self):
        image = create_image("pallete.png")
        expect(image).Not.to_be_null()
        expect(image.size).to_equal((3317, 2083))
