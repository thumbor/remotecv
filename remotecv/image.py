from io import BytesIO

from PIL import Image as PilImage

from remotecv.utils import config

DEFAULT_MAX_IMAGE_PIXELS = PilImage.MAX_IMAGE_PIXELS


class Image:
    @classmethod
    def create_from_buffer(cls, image_buffer):
        instance = cls()
        return instance.parse_image(image_buffer)

    def parse_image(self, image_buffer):
        limit = getattr(config, "max_image_pixels", DEFAULT_MAX_IMAGE_PIXELS)
        # Pillow refuses images above twice its own MAX_IMAGE_PIXELS, so it
        # has to follow the configured limit for 0 or a higher limit to work.
        PilImage.MAX_IMAGE_PIXELS = limit or None
        try:
            img = PilImage.open(BytesIO(image_buffer))
            if hasattr(img, "is_animated") and img.is_animated:
                return None
        except (IOError, PilImage.DecompressionBombError):
            return None
        if limit and img.width * img.height > limit:
            return None
        try:
            img.load()
        except PilImage.DecompressionBombError:
            # Containers such as ICNS only size their embedded image here.
            return None
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
