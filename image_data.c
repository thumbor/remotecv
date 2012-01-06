#include <stdio.h>

#include "remotecv_ss.h"
#include "bson/bson.h"

void copy_bson_bin(char **destination, int *dest_sz, bson_type type, bson_iterator *it)
{
    int len = bson_iterator_bin_len(it);
    const char *origin;

    *destination = malloc(sizeof(char) * len);
    
    if (type == bson_string) {
        origin = bson_iterator_string(it);
    } else if (type == bson_bindata) {
        origin = bson_iterator_bin_data(it);
    }

    *dest_sz = len;
    memcpy(*destination, origin, len);
}

void copy_bson_string(char **destination, bson_type type, bson_iterator *it)
{
    int len = bson_iterator_bin_len(it) + 1;
    *destination = malloc(sizeof(char) * len);

    if (type == bson_string) {
        strlcpy(*destination, bson_iterator_string(it), len);
    } else if (type == bson_bindata) {
        memcpy(*destination, bson_iterator_bin_data(it), len - 1);
        (*destination)[len - 1] = 0;
    }
}

void copy_bson_int(int *v, bson_type type, bson_iterator *it)
{
    if (type != bson_int) {
        return;
    }
    *v = bson_iterator_int(it);
}

void copy_bson_array_items(int *v1, int *v2, bson_type type, bson_iterator *it)
{
    if (type != bson_array) {
        return;
    }
    const char *array_data = bson_iterator_value(it);
    bson_iterator a_it;

    bson_iterator_init(&a_it, array_data);

    copy_bson_int(v1, bson_iterator_next(&a_it), &a_it);
    copy_bson_int(v2, bson_iterator_next(&a_it), &a_it);
}

void parse_image_data(size_t msg_sz, void *msg_data, image_data *img_data)
{
    if (!img_data) {
        return;
    }

    bson msg_buffer = {0}, *msg = &msg_buffer;
    bson_iterator iterator;
    bson_type type;
    const char *key;

    msg = bson_init_safe(msg, (char*) msg_data, 0, msg_sz);
    if (!msg) {
        goto invalid_error;
    }

    bson_iterator_init(&iterator, msg->data);
    while ((type = bson_iterator_next(&iterator))) {
        key = bson_iterator_key(&iterator);
        if (strcmp(key, "type") == 0) {
            copy_bson_string(&img_data->type, type, &iterator);
        } else if (strcmp(key, "mode") == 0) {
            copy_bson_string(&img_data->mode, type, &iterator);
        } else if (strcmp(key, "path") == 0) {
            copy_bson_string(&img_data->path, type, &iterator);
        } else if (strcmp(key, "image") == 0) {
            copy_bson_bin(&img_data->image, &img_data->image_sz, type, &iterator);
        } else if (strcmp(key, "size") == 0) {
            copy_bson_array_items(&img_data->width, &img_data->height, type, &iterator);
        }
    }
    log_image_data(img_data);

    bson_destroy(msg);

    return;

invalid_error:
    log_verbose("Invalid bson message");
}

int fill_detection_data(image_data *img_data, void **reply_buffer)
{
    bson result_bson;
    bson_buffer buffer;
    detect_data *current_data = 0;
    detect_data zero_data = {0};
    int index = 0;
    int result_size = 0;

    if (!img_data) {
        return 0;
    }

    bson_buffer_init(&buffer);
    bson_append_start_array(&buffer, "points");

    current_data = img_data->detection_points;
    while (current_data) {
        if (memcmp(current_data, &zero_data, sizeof(detect_data)) == 0) {
            break;
        }

        char index_buffer[10] = {0};
        snprintf(index_buffer, 10, "%d", index);

        bson_append_start_array(&buffer, index_buffer);
        bson_append_double(&buffer, "0", current_data->top);
        bson_append_double(&buffer, "1", current_data->left);
        bson_append_int(&buffer, "2", current_data->width);
        bson_append_int(&buffer, "3", current_data->height);
        bson_append_finish_object(&buffer);

        ++current_data;
        ++index;
    }

    bson_append_finish_object(&buffer);
    bson_from_buffer(&result_bson, &buffer);

    if (verbose_flag) {
        log_verbose("Points found:");
        bson_print(&result_bson);
    }

    result_size = bson_size(&result_bson);
    *reply_buffer = malloc(result_size);
    memcpy(*reply_buffer, result_bson.data, result_size);

    bson_destroy(&result_bson);

    return result_size;
}

void free_image_data(image_data *img_data)
{
    if (!img_data) {
        return;
    }
    if (img_data->type) {
        free(img_data->type);
    }
    if (img_data->mode) {
        free(img_data->mode);
    }
    if (img_data->path) {
        free(img_data->path);
    }
    if (img_data->image) {
        free(img_data->image);
    }
    if (img_data->detection_points) {
        free(img_data->detection_points);
    }
}
