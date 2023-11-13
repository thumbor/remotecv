from io import BytesIO

from PIL import Image as PilImage

from remotecv.utils import config

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

        return self.clear_metadata(img)

    def clear_metadata(self, image):
        if (
            not hasattr(config, "clear_image_metadata")
            or not config.clear_image_metadata
        ):
            return image

        if hasattr(image, "tag"):
            image.tag.clear()

        if hasattr(image, "tag_v2"):
            image.tag_v2.clear()

        return image
