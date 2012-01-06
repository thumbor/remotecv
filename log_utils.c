#include <stdio.h>
#include <stdarg.h>

#include "remotecv_ss.h"

inline void log_verbose(char *format, ...)
{
    if (!verbose_flag) {
        return;
    }

    va_list list;
    va_start(list, format);
    vprintf(format, list);
    printf("\n");
    fflush(stdout);
    va_end(list);
}

inline void log_image_data(image_data *data)
{
    if (!verbose_flag) {
        return;
    }

    log_verbose(
        "Image data:\n"\
        "  type:   %s\n"\
        "  mode:   %s\n"\
        "  path:   %s\n"\
        "  image:  [%d bytes]\n"\
        "  width:  %d\n"\
        "  height: %d",
        data->type,
        data->mode,
        data->path,
        data->image_sz,
        data->width,
        data->height
    );

}