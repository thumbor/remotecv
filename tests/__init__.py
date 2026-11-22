from io import BytesIO
from os.path import dirname, join

import numpy as np
from PIL import Image as PilImage

from remotecv.image import Image


def read_fixture(path):
    with open(join(dirname(__file__), "fixtures", path), "rb") as fixt:
        return fixt.read()


def create_image(path):
    return Image.create_from_buffer(read_fixture(path))


def create_image_as(path, image_format):
    buffer = BytesIO()
    PilImage.open(BytesIO(read_fixture(path))).save(buffer, image_format)
    return Image.create_from_buffer(buffer.getvalue())


def read_gray_pixels(path):
    return np.asarray(PilImage.open(BytesIO(read_fixture(path))).convert("L"))


def create_image_from_pixels(pixels, image_format="PNG"):
    buffer = BytesIO()
    PilImage.fromarray(pixels).save(buffer, image_format)
    return Image.create_from_buffer(buffer.getvalue())


def create_16_bit_image(path, used_bits=16):
    pixels = read_gray_pixels(path).astype(np.uint16) << (used_bits - 8)
    return create_image_from_pixels(pixels)
