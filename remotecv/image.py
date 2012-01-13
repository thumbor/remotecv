import cv

class Image:
    @classmethod
    def create_from_raw_bytes(cls, size, mode, img_data):
        instance = cls()
        instance.set_image_data(size, mode, img_data)
        return instance

    @classmethod
    def create_from_buffer(cls, image_buffer):
        instance = cls()
        instance.set_image_buffer(image_buffer)
        return instance

    def set_image_buffer(self, image_buffer):
        buffer_len = len(image_buffer)
        imagefiledata = cv.CreateMatHeader(1, buffer_len, cv.CV_8UC1)
        cv.SetData(imagefiledata, image_buffer, buffer_len)
        self.image = cv.DecodeImage(imagefiledata, cv.CV_LOAD_IMAGE_COLOR)
        self.size = cv.GetSize(self.image)
        self.mode = "BGR"

    def set_image_raw_data(self, size, mode, img_data):
        self.image = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(self.image, img_data)
        self.mode = mode
        self.size = size

    def grayscale(self):
        convert_mode = getattr(cv, 'CV_%s2GRAY' % self.mode)

        gray = cv.CreateImage(self.size, cv.IPL_DEPTH_8U, 1)
        cv.CvtColor(self.image, gray, convert_mode)
        cv.EqualizeHist(gray, gray)
        self.image = gray
