import bson

from remotecv.image_processor import ImageProcessor

from remotecv.utils import logger

class RemoteCvApp:

    def __init__(self):
        self.processor = ImageProcessor()

    def process_request(self, msg):
        msg = bson.loads(msg)
        points = self.processor.detect(msg['type'], msg['size'], msg['mode'], msg['image'])
        return bson.dumps({ 'points': points })
