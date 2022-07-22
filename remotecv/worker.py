#!/usr/bin/python
# -*- coding: utf-8 -*-

# remote cv service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import logging
import sys
from http.server import HTTPServer
from importlib import import_module
from threading import Thread

import click
from click_option_group import optgroup

from remotecv.error_handler import ErrorHandler
from remotecv.healthcheck import HealthCheckHandler
from remotecv.importer import Importer
from remotecv.utils import config, redis_client, SINGLE_NODE, SENTINEL, context


def start_pyres_worker():
    from remotecv.unique_queue import (  # NOQA pylint: disable=import-outside-toplevel
        UniqueWorker,
    )

    redis = redis_client()

    def after_fork(_):
        config.error_handler.install_handler()

    worker = UniqueWorker(
        queues=["Detect"],
        server=redis,
        timeout=config.timeout,
        after_fork=after_fork,
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


def import_modules():
    Metrics = Importer.import_class("Metrics", config.metrics)
    context.metrics = Metrics(config)
    context.metrics.initialize()


@click.command()
@optgroup.group("Worker Backend")
@optgroup.option(
    "-b",
    "--backend",
    envvar="BACKEND",
    show_envvar=True,
    default="pyres",
    type=click.Choice(["pyres", "celery"]),
    help="Worker backend",
)
@optgroup.group("Pyres Connection Arguments")
@optgroup.option(
    "--host",
    envvar="REDIS_HOST",
    show_envvar=True,
    default="localhost",
    help="Redis host",
)
@optgroup.option(
    "--port",
    envvar="REDIS_PORT",
    show_envvar=True,
    default=6379,
    help="Redis port",
)
@optgroup.option(
    "--database",
    envvar="REDIS_DATABASE",
    show_envvar=True,
    default=0,
    help="Redis database",
)
@optgroup.option(
    "--password",
    envvar="REDIS_PASSWORD",
    show_envvar=True,
    default=None,
    help="Redis password",
)
@optgroup.option(
    "--redis-mode",
    envvar="REDIS_MODE",
    show_envvar=True,
    default=SINGLE_NODE,
    type=click.Choice([SINGLE_NODE, SENTINEL]),
    help="Redis mode",
)
@optgroup.option(
    "--sentinel-instances",
    envvar="REDIS_SENTINEL_INSTANCES",
    show_envvar=True,
    default="localhost:26376",
    help="Redis Sentinel instances e.g. 'localhost:26376,localhost:26377'",
)
@optgroup.option(
    "--sentinel-password",
    envvar="REDIS_SENTINEL_PASSWORD",
    show_envvar=True,
    default=None,
    help="Redis Sentinel password",
)
@optgroup.option(
    "--master-instance",
    envvar="REDIS_MASTER_INSTANCE",
    show_envvar=True,
    default=None,
    help="Redis Sentinel master instance",
)
@optgroup.option(
    "--master-password",
    envvar="REDIS_MASTER_PASSWORD",
    show_envvar=True,
    default=None,
    help="Redis Sentinel master password",
)
@optgroup.option(
    "--master-database",
    envvar="REDIS_MASTER_DATABASE",
    show_envvar=True,
    default=0,
    help="Redis Sentinel master database",
)
@optgroup.option(
    "--socket-timeout",
    envvar="REDIS_SENTINEL_SOCKET_TIMEOUT",
    show_envvar=True,
    default=10.0,
    help="Redis Sentinel socket timeout",
)
@optgroup.group("Celery/SQS Connection Arguments")
@optgroup.option(
    "--region",
    envvar="AWS_REGION",
    show_envvar=True,
    default="us-east-1",
    help="AWS SQS Region",
)
@optgroup.option(
    "--key-id",
    envvar="AWS_ACCESS_KEY_ID",
    show_envvar=True,
    default=None,
    help="AWS access key id",
)
@optgroup.option(
    "--key-secret",
    envvar="AWS_SECRET_ACCESS_KEY",
    show_envvar=True,
    default=None,
    help="AWS access key secret",
)
@optgroup.option(
    "--polling-interval",
    envvar="SQS_POLLING_INTERVAL",
    show_envvar=True,
    default=20,
    help="AWS polling interval",
)
@optgroup.option(
    "--celery-commands",
    envvar="CELERY_COMMANDS",
    show_envvar=True,
    default=[],
    multiple=True,
    help="SQS command",
)
@optgroup.group("Other arguments")
@optgroup.option(
    "--server-port",
    envvar="HTTP_SERVER_PORT",
    show_envvar=True,
    default=8080,
    help="HTTP server port",
)
@optgroup.option(
    "--with-healthcheck",
    envvar="WITH_HEALTHCHECK",
    show_envvar=True,
    is_flag=True,
    default=False,
    help="Start a healthcheck http endpoint",
)
@optgroup.option(
    "-l",
    "--level",
    envvar="LOG_LEVEL",
    show_envvar=True,
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    default="debug",
    help="Logging level",
)
@optgroup.option(
    "-f",
    "--format",
    envvar="LOG_FORMAT",
    show_envvar=True,
    default="%(asctime)s %(name)s:%(levelname)s %(message)s",
    help="Logging format",
)
@optgroup.option(
    "-o",
    "--loader",
    envvar="IMAGE_LOADER",
    show_envvar=True,
    default="remotecv.http_loader",
    help="Image loader",
)
@optgroup.option(
    "-s",
    "--store",
    envvar="DETECTOR_STORAGE",
    show_envvar=True,
    default="remotecv.result_store.redis_store",
    help="Detector result store",
)
@optgroup.option(
    "-t",
    "--timeout",
    envvar="DETECTOR_TIMEOUT",
    show_envvar=True,
    default=None,
    type=click.INT,
    help="Timeout in seconds for image detection",
)
@optgroup.option(
    "--sentry-url",
    envvar="SENTRY_URL",
    show_envvar=True,
    default=None,
    help="Sentry URL",
)
@optgroup.option(
    "--metrics",
    envvar="METRICS_CLIENT",
    show_envvar=True,
    default="remotecv.metrics.logger_metrics",
    help="Metrics client, should be the full name of a python module",
)
@optgroup.group("Memcached store arguments")
@optgroup.option(
    "--memcached-hosts",
    envvar="MEMCACHED_HOSTS",
    show_envvar=True,
    default="localhost:11211",
    help="Comma separated list of memcached hosts",
)
def main(**params):
    """Runs RemoteCV"""

    logging.basicConfig(level=getattr(logging, params["level"].upper()), format=params["format"])

    config.backend = params["backend"]
    config.redis_host = params["host"]
    config.redis_port = params["port"]
    config.redis_database = params["database"]
    config.redis_password = params["password"]
    config.redis_mode = params["redis_mode"]
    config.redis_sentinel_instances = params["sentinel_instances"]
    config.redis_sentinel_password = params["sentinel_password"]
    config.redis_sentinel_socket_timeout = params["socket_timeout"]
    config.redis_sentinel_master_instance = params["master_instance"]
    config.redis_sentinel_master_password = params["master_password"]
    config.redis_sentinel_master_database = params["master_database"]

    config.region = params["region"]
    config.key_id = params["key_id"]
    config.key_secret = params["key_secret"]
    config.polling_interval = params["polling_interval"]

    config.timeout = params["timeout"]
    config.server_port = params["server_port"]
    config.log_level = params["level"].upper()
    config.loader = import_module(params["loader"])
    config.store = import_module(params["store"])

    config.metrics = params["metrics"]

    config.memcache_hosts = params["memcached_hosts"]

    config.extra_args = sys.argv[:1] + list(params["celery_commands"])

    config.error_handler = ErrorHandler(params["sentry_url"])

    import_modules()

    if params["with_healthcheck"]:
        start_http_server()

    if params["backend"] == "pyres":
        start_pyres_worker()
    elif params["backend"] == "celery":
        start_celery_worker()


if __name__ == "__main__":
    main()
