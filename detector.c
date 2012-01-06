#include <opencv/cv.h>
#include <math.h>

#include "remotecv_ss.h"

#define FACE_CASCADE_FILE "cascades/haarcascade_frontalface_alt.xml"

CvHaarClassifierCascade* load_object_detector(const char* cascade_path)
{
    return (CvHaarClassifierCascade*)cvLoad(cascade_path, NULL, NULL, NULL);
}

int get_conversion_mode(char *mode)
{
    if (strcmp(mode, "BGR") == 0) {
        return CV_BGR2GRAY;
    }
    return CV_RGB2GRAY;
}

int get_min_size_for(int width, int height)
{
    int ratio = MIN(width, height) / 15;
    ratio = MAX(20, ratio);
    return ratio;
}

CvHaarClassifierCascade* g_face_cascade = 0;

void detect_features(image_data *img_data)
{
    if (!img_data) {
        return;
    }

    CvHaarClassifierCascade *cascade_file;
    IplImage *image, *gray_image;
    CvSeq* faces;
    CvMemStorage* storage;

    int faces_idx;
    int min_size = 0;
    double haar_scale = 1.2;
    int min_neighbors = 1;

    if (strcmp(img_data->type, "face") == 0) {
        if (!g_face_cascade) {
            g_face_cascade = load_object_detector(FACE_CASCADE_FILE);
        }
        cascade_file = g_face_cascade;
    }

    image = cvCreateImageHeader(cvSize(img_data->width, img_data->height), IPL_DEPTH_8U, 3);
    gray_image = cvCreateImage(cvSize(img_data->width, img_data->height), 8, 1);

    cvSetData(image, img_data->image, img_data->width * 3);

    cvCvtColor(image, gray_image, get_conversion_mode(img_data->mode));
    cvEqualizeHist(gray_image, gray_image);

    min_size = get_min_size_for(img_data->width, img_data->height);
    storage = cvCreateMemStorage(0);
    faces = cvHaarDetectObjects(gray_image, cascade_file, storage, 
                                haar_scale, min_neighbors, CV_HAAR_DO_CANNY_PRUNING,
                                cvSize(min_size, min_size), cvSize(0, 0));


    int buffer_size = sizeof(detect_data) * (faces->total + 1);
    img_data->detection_points = (detect_data *)malloc(buffer_size);
    memset(img_data->detection_points, 0, buffer_size);

    for (faces_idx = 0; faces_idx < faces->total; ++faces_idx) {
        CvRect *face_rect = (CvRect*)cvGetSeqElem(faces, faces_idx);

        img_data->detection_points[faces_idx].top    = face_rect->x;
        img_data->detection_points[faces_idx].left   = face_rect->y;
        img_data->detection_points[faces_idx].width  = face_rect->width;
        img_data->detection_points[faces_idx].height = face_rect->height;
    }

    cvReleaseImage(&gray_image);
    cvReleaseMemStorage(&storage);
    cvReleaseImageHeader(&image);

}
