#!/usr/bin/python
# -*- coding: utf-8 -*-

# remote cv service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import argparse
import logging
import sys
from http.server import HTTPServer
from importlib import import_module
from threading import Thread

from remotecv.error_handler import ErrorHandler
from remotecv.utils import config, redis_client, SINGLE_NODE, SENTINEL
from remotecv.healthcheck import HealthCheckHandler


def start_pyres_worker():
    from remotecv.unique_queue import (  # NOQA pylint: disable=import-outside-toplevel
        UniqueWorker,
    )

    redis = redis_client()

    def after_fork(_):
        config.error_handler.install_handler()

    worker = UniqueWorker(
        queues=["Detect"], server=redis, timeout=config.timeout, after_fork=after_fork
    )
    worker.work()


def start_celery_worker():
    from remotecv.celery_tasks import (  # NOQA pylint: disable=import-outside-toplevel
        CeleryTasks,
    )

    celery_tasks = CeleryTasks(
        config.key_id,
        config.key_secret,
        config.region,
        config.timeout,
        config.polling_interval,
    )
    celery_tasks.run_commands(config.extra_args, log_level=config.log_level)


def start_http_server():
    def serve_forever(httpd):
        with httpd:
            httpd.serve_forever()

    httpd = HTTPServer(("", config.server_port), HealthCheckHandler)

    thread = Thread(target=serve_forever, args=(httpd,))
    thread.setDaemon(True)
    thread.start()


def main(params=None):
    if params is None:
        params = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Runs RemoteCV.")

    conn_group = parser.add_argument_group("Worker Backend")
    conn_group.add_argument(
        "-b",
        "--backend",
        default="pyres",
        choices=["pyres", "celery"],
        help="Worker backend",
    )

    conn_group = parser.add_argument_group("Pyres Connection Arguments")
    conn_group.add_argument("--host", default="localhost", help="Redis host")
    conn_group.add_argument("--port", default=6379, type=int, help="Redis port")
    conn_group.add_argument("--database", default=0, type=int, help="Redis database")
    conn_group.add_argument("--password", default=None, help="Redis password")
    conn_group.add_argument(
        "--redis-mode",
        default=SINGLE_NODE,
        choices=[SINGLE_NODE, SENTINEL],
        help="Redis mode",
    )
    conn_group.add_argument(
        "--sentinel-instances",
        default="localhost:26376",
        help="Redis Sentinel instances e.g. 'localhost:26376,localhost:26377'",
    )
    conn_group.add_argument(
        "--sentinel-password", default=None, help="Redis Sentinel password"
    )
    conn_group.add_argument(
        "--master-instance", default=None, help="Redis Sentinel master instance"
    )
    conn_group.add_argument(
        "--master-password", default=None, help="Redis Sentinel master password"
    )
    conn_group.add_argument(
        "--master-database",
        default=0,
        type=int,
        help="Redis Sentinel master database",
    )
    conn_group.add_argument(
        "--socket-timeout",
        default=10.0,
        type=float,
        help="Redis Sentinel socket timeout",
    )

    conn_group = parser.add_argument_group("Celery/SQS Connection Arguments")
    conn_group.add_argument("--region", default="us-east-1", help="AWS SQS Region")
    conn_group.add_argument("--key_id", default="", help="AWS access key id")
    conn_group.add_argument("--key_secret", default="", help="AWS access key secret")
    conn_group.add_argument(
        "--polling_interval", default=20, help="AWS polling interval"
    )

    other_group = parser.add_argument_group("Other arguments")
    other_group.add_argument(
        "--server-port", default=8080, type=int, help="Server http port"
    )
    other_group.add_argument(
        "--with-healthcheck",
        default=False,
        action='store_true',
        help="Start an healthchecker http endpoint",
    )
    other_group.add_argument("-l", "--level", default="debug", help="Logging level")
    other_group.add_argument(
        "-o", "--loader", default="remotecv.http_loader", help="Loader used"
    )
    other_group.add_argument(
        "-s", "--store", default="remotecv.result_store.redis_store", help="Loader used"
    )
    other_group.add_argument(
        "-t",
        "--timeout",
        default=None,
        type=int,
        help="Timeout in seconds for image detection",
    )
    other_group.add_argument(
        "--sentry_url", default=None, help="URL used to send errors to sentry"
    )

    memcache_store_group = parser.add_argument_group("Memcache store arguments")
    memcache_store_group.add_argument(
        "--memcache_hosts",
        default="localhost:11211",
        help="Comma separated list of memcache hosts",
    )

    parser.add_argument("args", nargs=argparse.REMAINDER)

    arguments = parser.parse_args(params)
    logging.basicConfig(level=getattr(logging, arguments.level.upper()))

    config.backend = arguments.backend
    config.redis_host = arguments.host
    config.redis_port = arguments.port
    config.redis_database = arguments.database
    config.redis_password = arguments.password
    config.redis_mode = arguments.redis_mode
    config.redis_sentinel_instances = arguments.sentinel_instances
    config.redis_sentinel_password = arguments.sentinel_password
    config.redis_sentinel_socket_timeout = arguments.socket_timeout
    config.redis_sentinel_master_instance = arguments.master_instance
    config.redis_sentinel_master_password = arguments.master_password
    config.redis_sentinel_master_database = arguments.master_database

    config.region = arguments.region
    config.key_id = arguments.key_id
    config.key_secret = arguments.key_secret
    config.polling_interval = arguments.polling_interval

    config.timeout = arguments.timeout
    config.server_port = arguments.server_port
    config.log_level = arguments.level.upper()
    config.loader = import_module(arguments.loader)
    config.store = import_module(arguments.store)

    config.memcache_hosts = arguments.memcache_hosts

    config.extra_args = sys.argv[:1] + arguments.args

    config.error_handler = ErrorHandler(arguments.sentry_url)

    if arguments.with_healthcheck:
        start_http_server()

    if arguments.backend == "pyres":
        start_pyres_worker()
    elif arguments.backend == "celery":
        start_celery_worker()


if __name__ == "__main__":
    main()
