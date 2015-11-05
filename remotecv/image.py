from io import BytesIO

from PIL import Image as PilImage

PilImage.IGNORE_DECODING_ERRORS = True
PilImage.MAXBLOCK = 2 ** 25


class Image:
    @classmethod
    def create_from_buffer(cls, image_buffer):
        instance = cls()
        if not instance.is_valid(image_buffer):
            return None

        return instance.parse_image(image_buffer)

    def is_valid(self, image_buffer):
        return len(image_buffer) > 4 and image_buffer[:4] != 'GIF8'

    def parse_image(self, image_buffer):
        tmp = BytesIO(image_buffer)
        img = PilImage.open(tmp)
        try:
            img.load()
        except IOError:
            pass
        img = img.convert('L')
        tmp.close()
        return img
