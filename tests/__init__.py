from os.path import dirname, join

from remotecv.image import Image


def read_fixture(path):
    with open(join(dirname(__file__), "fixtures", path), "rb") as fixt:
        return fixt.read()


def create_image(path):
    return Image.create_from_buffer(read_fixture(path))
