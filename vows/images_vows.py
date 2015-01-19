from pyvows import Vows, expect
from . import read_fixture

from remotecv.image import Image


@Vows.batch
class ImageVows(Vows.Context):

    class WhenReadingAPSD(Vows.Context):
        def topic(self):
            return Image.create_from_buffer(read_fixture('why_not_a.psd'))

        def should_be_ok(self, topic):
            expect(topic.image).Not.to_be_null()
            expect(topic.size).to_equal((620, 413))

    class WhenReadingABrokenJpg(Vows.Context):
        def topic(self):
            return Image.create_from_buffer(read_fixture('broken.jpg'))

        def should_be_ok(self, topic):
            expect(topic.image).Not.to_be_null()
            expect(topic.size).to_equal((600, 769))
