#include <zmq.h>
#include <stdio.h>
#include <getopt.h>
#include <sys/time.h>

#include "remotecv_ss.h"

int verbose_flag;

void run_server(const app_options *opts)
{
    void *context = zmq_init(1);
    void *socket = zmq_socket(context, ZMQ_REP);
    char connect_url[MAX_URL_SZ] = {0};
    struct timeval start_time = {0}, end_time = {0};

    snprintf(connect_url, MAX_URL_SZ, "tcp://%s:%hu", opts->bind_addr, opts->port);

    log_verbose("Listening connections at %s", connect_url);

    zmq_bind(socket, connect_url);

    while (1) {
        zmq_msg_t request_msg, reply_msg;
        void *reply_buffer = 0;
        int reply_size = 0;
        image_data img_data = {0};

        zmq_msg_init(&request_msg);
        zmq_recv(socket, &request_msg, 0);
        log_verbose("Message received, processing...");
        if (verbose_flag) {
            gettimeofday(&start_time, NULL);
        }

        parse_image_data(zmq_msg_size(&request_msg), zmq_msg_data(&request_msg), &img_data);
        detect_features(&img_data);
        reply_size = fill_detection_data(&img_data, &reply_buffer);
        free_image_data(&img_data);

        zmq_msg_close(&request_msg);

        if (!reply_buffer) {
            reply_size = 0;
        }
        zmq_msg_init_size(&reply_msg, reply_size);
        if (reply_size) {
            memcpy(zmq_msg_data(&reply_msg), reply_buffer, reply_size);
            free(reply_buffer);
        }
        if (verbose_flag) {
            gettimeofday(&end_time, NULL);
            long long diff = 
                (((long long) end_time.tv_sec) * 1000000 + end_time.tv_usec) -
                (((long long) start_time.tv_sec) * 1000000 + start_time.tv_usec);
            log_verbose("Sending reply. Ellapsed: %lldms", diff / 1000);
        }
        zmq_send(socket, &reply_msg, 0);
        zmq_msg_close(&reply_msg);
    }

    zmq_close(socket);
    zmq_term(context);
}

void print_help(char *command)
{
    printf(
        "Usage: %s [-b bind_addr] [-p port] [-v]\n"\
        "\t-b --bind ADDR                Bind address, defaults to %s\n"\
        "\t-p --port PORT                Port to listen, defaults to %hu\n"\
        "\t-v --verbose                  Prints lots of stuff\n",

        command, DEFAULT_BIND_ADDR, DEFAULT_PORT
    );
}

void parse_args(int argc, char **argv, app_options *opts)
{
    struct option long_options[] = 
        {
            {"verbose", no_argument,       &verbose_flag, 1},
            {"bind",    required_argument, 0, 'b'},
            {"port",    required_argument, 0, 'p'},
            {"help",    no_argument,       0, 'h'},
            {0, 0, 0, 0}
        };
 
    int option_index = 0, ch;

    if (!opts) {
        return;
    }

    while ((ch = getopt_long(argc, argv, "vhb:p:", long_options, &option_index)) != -1) {
        switch (ch) {
            case 'v':
                verbose_flag = 1;
                break;
            case 'b':
                strlcpy(opts->bind_addr, optarg, MAX_BIND_ADDR_SZ);
                break;
            case 'p':
                opts->port = (unsigned short)atoi(optarg);
                break;
            case 'h':
            case '?':
                print_help(argv[0]);
                exit(0);
                break;
            default:
                break;
        }
    }

}

int main(int argc, char **argv)
{
    app_options opts = {
        DEFAULT_BIND_ADDR, DEFAULT_PORT
    };
    parse_args(argc, argv, &opts);
    run_server(&opts);
    return 0;
}
