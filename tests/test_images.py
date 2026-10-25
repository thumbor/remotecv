import struct
import warnings
from io import BytesIO
from unittest import TestCase

from PIL import Image as PilImage

from remotecv.image import DEFAULT_MAX_IMAGE_PIXELS, Image
from remotecv.utils import config
from tests import create_image


def png_with_size(width, height):
    buffer = BytesIO()
    PilImage.new("1", (width, height)).save(buffer, "PNG")
    return buffer.getvalue()


def icns_with_png(png):
    block = b"ic07" + struct.pack(">I", 8 + len(png)) + png
    return b"icns" + struct.pack(">I", 8 + len(block)) + block


class ImageTest(TestCase):
    def tearDown(self):
        if hasattr(config, "max_image_pixels"):
            del config.max_image_pixels
        PilImage.MAX_IMAGE_PIXELS = DEFAULT_MAX_IMAGE_PIXELS

    def test_should_read_a_psd(self):
        image = create_image("why_not_a.psd")
        assert image is not None
        assert image.size == (620, 413)

    def test_when_image_is_broken(self):
        image = create_image("broken.jpg")
        assert image is not None
        assert image.size == (600, 769)

    def test_when_image_is_pallete(self):
        image = create_image("pallete.png")
        assert image is not None
        assert image.size == (3317, 2083)

    def test_should_clear_image_metadata(self):
        config.clear_image_metadata = True
        image = create_image("with_metadata.tiff")
        assert image is not None
        assert image.tag == {}
        assert image.tag_v2 == {}
        assert image.size == (41, 48)

    def test_should_not_clear_image_metadata(self):
        config.clear_image_metadata = False
        image = create_image("with_metadata.tiff")
        assert image is not None
        assert image.tag != {}
        assert image.tag_v2 != {}
        assert image.size == (41, 48)

    def test_should_reject_decompression_bomb(self):
        side = int((DEFAULT_MAX_IMAGE_PIXELS * 2) ** 0.5) + 1
        image = Image.create_from_buffer(png_with_size(side, side))
        assert image is None

    def test_should_reject_decompression_bomb_found_while_loading(self):
        side = int((DEFAULT_MAX_IMAGE_PIXELS * 2) ** 0.5) + 1
        buffer = icns_with_png(png_with_size(side, side))
        image = Image.create_from_buffer(buffer)
        assert image is None

    def test_should_reject_image_above_default_pixel_limit(self):
        side = int(DEFAULT_MAX_IMAGE_PIXELS**0.5) + 1
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", PilImage.DecompressionBombWarning)
            image = Image.create_from_buffer(png_with_size(side, side))
        assert image is None

    def test_should_reject_image_above_configured_pixel_limit(self):
        config.max_image_pixels = 100 * 100 - 1
        image = Image.create_from_buffer(png_with_size(100, 100))
        assert image is None

    def test_should_accept_image_within_configured_pixel_limit(self):
        config.max_image_pixels = 100 * 100
        image = Image.create_from_buffer(png_with_size(100, 100))
        assert image is not None
        assert image.size == (100, 100)

    def test_should_accept_any_size_when_limit_is_zero(self):
        config.max_image_pixels = 0
        side = int((DEFAULT_MAX_IMAGE_PIXELS * 2) ** 0.5) + 1
        image = Image.create_from_buffer(png_with_size(side, side))
        assert image is not None

    def test_should_accept_image_above_pillow_limit_when_raised(self):
        config.max_image_pixels = DEFAULT_MAX_IMAGE_PIXELS * 4
        side = int((DEFAULT_MAX_IMAGE_PIXELS * 2) ** 0.5) + 1
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", PilImage.DecompressionBombWarning)
            image = Image.create_from_buffer(png_with_size(side, side))
        assert image is not None
