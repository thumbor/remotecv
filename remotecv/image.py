import cv

class Image:
    def __init__(self, img_buffer):
        buffer_len = len(img_buffer)
        imagefiledata = cv.CreateMatHeader(1, buffer_len, cv.CV_8UC1)
        cv.SetData(imagefiledata, img_buffer, buffer_len)
        self.image = cv.DecodeImage(imagefiledata, cv.CV_LOAD_IMAGE_COLOR)

    def size(self):
        return cv.GetSize(self.image)

    def grayscale(self):
        gray = cv.CreateImage(self.size(), cv.IPL_DEPTH_8U, 1)
        cv.CvtColor(self.image, gray, cv.CV_BGR2GRAY)
        cv.EqualizeHist(gray, gray)
        self.image = gray

    def crop(self, left, top, right, bottom):
        if left == 0 and top == 0 and right == 0 and bottom == 0:
            return

        limit = lambda dimension, maximum: min(max(dimension, 0), maximum)
        width, height = self.size()

        left = limit(left, width)
        top = limit(top, height)
        right = limit(right, width)
        bottom = limit(bottom, height)

        if left >= right or top >= bottom:
            return

        new_width = right - left
        new_height = bottom - top

        cropped = cv.CreateImage((new_width, new_height), cv.IPL_DEPTH_8U, self.image.nChannels)

        src_region = cv.GetSubRect(self.image, (left, top, new_width, new_height))
        cv.Copy(src_region, cropped)

        self.image = cropped
