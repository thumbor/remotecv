from unittest import TestCase

from preggy import expect

from remotecv.utils import config
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

    def test_should_clear_image_metadata(self):
        config.clear_image_metadata = True
        image = create_image("with_metadata.tiff")
        expect(image).Not.to_be_null()
        expect(image.tag).to_equal({})
        expect(image.tag_v2).to_equal({})
        expect(image.size).to_equal((41, 48))

    def test_should_not_clear_image_metadata(self):
        config.clear_image_metadata = False
        image = create_image("with_metadata.tiff")
        expect(image).Not.to_be_null()
        expect(image.tag).Not.to_equal({})
        expect(image.tag_v2).Not.to_equal({})
        expect(image.size).to_equal((41, 48))
