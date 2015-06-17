from pyvows import Vows, expect
from . import read_fixture

from remotecv.image_processor import ImageProcessor


@Vows.batch
class ImageProcessorVows(Vows.Context):

    class WhenDetectorUnavailable(Vows.Context):

        @Vows.capture_error
        def topic(self):
            image_processor = ImageProcessor()
            return image_processor.detect('feat', read_fixture('broken.jpg'))

        def should_raise_error(self, topic):
            expect(topic).to_be_an_error_like(AttributeError)

    class WhenDetectorAvailable(Vows.Context):

        def topic(self):
            image_processor = ImageProcessor()
            for detector in ['all', 'face', 'feature', 'glass', 'profile']:
                yield image_processor.detect(detector, read_fixture('broken.jpg'))

        def should_detect(self, topic):
            expect(topic).Not.to_be_empty()
