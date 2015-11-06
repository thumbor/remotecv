from os.path import join, dirname
from remotecv.image import Image


def read_fixture(path):
    with open(join(dirname(__file__), 'fixtures', path)) as f:
        return f.read()


def create_image(path):
    return Image.create_from_buffer(read_fixture(path))
