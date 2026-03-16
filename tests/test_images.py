from io import BytesIO
from unittest import TestCase, mock

from PIL import Image as PilImage
from preggy import expect

from remotecv.image import Image
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

    def test_should_handle_ioerror_on_image_load(self):
        pil_img = mock.MagicMock(spec=PilImage.Image)
        pil_img.is_animated = False
        pil_img.load.side_effect = IOError("truncated")

        with mock.patch("remotecv.image.PilImage.open", return_value=pil_img):
            img = Image.create_from_buffer(b"data")

        # Should still return the image (IOError on load is non-fatal)
        expect(img).not_to_be_null()

    def test_should_clear_metadata_without_tag_attributes(self):
        config.clear_image_metadata = True
        pil_img = mock.MagicMock(spec=PilImage.Image)
        # spec=PilImage.Image means hasattr checks use the real class attrs;
        # delete them on the instance to exercise the False branches
        del pil_img.tag
        del pil_img.tag_v2
        pil_img.is_animated = False
        pil_img.load.return_value = None

        with mock.patch("remotecv.image.PilImage.open", return_value=pil_img):
            img = Image.create_from_buffer(b"data")

        expect(img).not_to_be_null()
