from io import BytesIO

from PIL import Image as PilImage

PilImage.IGNORE_DECODING_ERRORS = True
PilImage.MAXBLOCK = 2**25


class Image:
    @classmethod
    def create_from_buffer(cls, image_buffer):
        instance = cls()
        return instance.parse_image(image_buffer)

    def parse_image(self, image_buffer):
        try:
            img = PilImage.open(BytesIO(image_buffer))
            if hasattr(img, "is_animated") and img.is_animated:
                return None
        except IOError:
            return None
        try:
            img.load()
        except IOError:
            pass
        return img
