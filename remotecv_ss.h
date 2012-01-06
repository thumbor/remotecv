#ifndef __REMOTECV_SS_H__
#define __REMOTECV_SS_H__

#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define DEFAULT_BIND_ADDR "*"
#define DEFAULT_PORT 13337

extern int verbose_flag;

#define MAX_BIND_ADDR_SZ 255
#define MAX_URL_SZ 270

typedef struct app_options {
    char bind_addr[MAX_BIND_ADDR_SZ];
    unsigned short port;
} app_options;

typedef struct detect_data {
    double top;
    double left;

    int width;
    int height;
} detect_data;

typedef struct image_data {
    int width;
    int height;

    char *type;
    char *mode;
    char *path;

    char *image;
    int image_sz;

    detect_data *detection_points;
} image_data;


// image_data.c functions
void parse_image_data(size_t msg_sz, void *msg_data, image_data *img_data);
void free_image_data(image_data *img_data);
int fill_detection_data(image_data *img_data, void **reply_buffer);

// detector.c functions
void detect_features(image_data *img_data);

// log_utils.c functions
inline void log_verbose(char *msg, ...);
inline void log_image_data(image_data *data);


#endif
