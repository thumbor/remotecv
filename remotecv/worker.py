# -*- coding: utf-8 -*-

# remote cv service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import logging
import math
import os
from importlib import import_module
from importlib.util import find_spec
from threading import Thread
from urllib.parse import quote

import click
from click_option_group import optgroup

from remotecv.celery_tasks import (
    CeleryTasks,
    CeleryUniqueQueue,
    build_sqs_broker,
)
from remotecv.error_handler import ErrorHandler
from remotecv.healthcheck import HealthCheckHandler, HealthCheckServer
from remotecv.http_loader import DEFAULT_USER_AGENT
from remotecv.image import DEFAULT_MAX_IMAGE_PIXELS
from remotecv.importer import Importer
from remotecv.utils import SENTINEL, SINGLE_NODE, config, context, redis_client


def _redis_url_auth(password):
    if not password:
        return ""
    return f":{quote(password, safe='')}@"


def _build_redis_broker_url():
    if config.redis_mode == SENTINEL:
        auth = _redis_url_auth(config.redis_sentinel_master_password)
        db = config.redis_sentinel_master_database
        return ";".join(
            f"sentinel://{auth}{instance}/{db}"
            for instance in config.redis_sentinel_instances.split(",")
        )
    auth = _redis_url_auth(config.redis_password)
    host = f"{config.redis_host}:{config.redis_port}"
    return f"redis://{auth}{host}/{config.redis_database}"


def _build_redis_broker_transport_options():
    if config.redis_mode != SENTINEL:
        return None
    options = {"master_name": config.redis_sentinel_master_instance}
    if config.redis_sentinel_password:
        options["sentinel_kwargs"] = {
            "password": config.redis_sentinel_password
        }
    return options


def start_celery_worker():
    celery_tasks = CeleryTasks(
        config.broker_url,
        config.broker_transport_options,
        unique_queue=CeleryUniqueQueue(redis_client()),
        time_limit=config.timeout,
    )
    celery_tasks.run_commands(config.extra_args, log_level=config.log_level)


def start_http_server():
    def serve_forever(httpd):
        with httpd:
            httpd.serve_forever()

    httpd = HealthCheckServer(
        (config.server_host, config.server_port), HealthCheckHandler
    )

    thread = Thread(target=serve_forever, args=(httpd,))
    thread.daemon = True
    thread.start()
    return httpd


def finite_only(_ctx, _param, value):
    if not math.isfinite(value):
        raise click.BadParameter(f"{value} is not a finite number")
    return value


def non_empty_printable_ascii(_ctx, _param, value):
    if not (value and value.isascii() and value.isprintable()):
        raise click.BadParameter(
            f"{value!r} must be non-empty printable ASCII"
        )
    return value


def import_modules():
    Metrics = Importer.import_class("Metrics", config.metrics)
    context.metrics = Metrics(config)
    context.metrics.initialize()


@click.command()
@optgroup.group("Redis Connection Arguments")
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
    "--redis-key-expire-time",
    envvar="REDIS_KEY_EXPIRE_TIME",
    show_envvar=True,
    default=1209600,
    help="Redis key expiration time in seconds",
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
@optgroup.group("Celery Connection Arguments")
@optgroup.option(
    "--broker",
    envvar="CELERY_BROKER",
    show_envvar=True,
    default="redis",
    type=click.Choice(["sqs", "redis"]),
    help="Celery broker backend",
)
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
    "--server-host",
    envvar="HTTP_SERVER_HOST",
    show_envvar=True,
    default="0.0.0.0",
    help="HTTP server bind address",
)
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
    "--loader-timeout",
    envvar="IMAGE_LOADER_TIMEOUT",
    show_envvar=True,
    default=20.0,
    type=click.FloatRange(min=0, min_open=True),
    callback=finite_only,
    help="Timeout in seconds for fetching the original image",
)
@optgroup.option(
    "--loader-max-body-size",
    envvar="IMAGE_LOADER_MAX_BODY_SIZE",
    show_envvar=True,
    default=0,
    type=click.IntRange(min=0),
    help="Maximum size in bytes of the original image (0 for no limit)",
)
@optgroup.option(
    "--loader-user-agent",
    envvar="IMAGE_LOADER_USER_AGENT",
    show_envvar=True,
    default=DEFAULT_USER_AGENT,
    callback=non_empty_printable_ascii,
    help="User-Agent header sent when fetching the original image",
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
    type=click.IntRange(min=0),
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
@optgroup.option(
    "--clear-image-metadata",
    envvar="CLEAR_IMAGE_METADATA",
    show_envvar=True,
    is_flag=True,
    default=False,
    help="Clears metadata when loading image",
)
@optgroup.option(
    "--max-image-pixels",
    envvar="MAX_IMAGE_PIXELS",
    show_envvar=True,
    default=DEFAULT_MAX_IMAGE_PIXELS,
    type=click.IntRange(min=0),
    help="Skip images with more pixels than this (0 for no limit)",
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

    if os.environ.get("BACKEND"):
        raise click.UsageError(
            "BACKEND is no longer supported, use --broker or CELERY_BROKER"
        )

    logging.basicConfig(
        level=getattr(logging, params["level"].upper()),
        format=params["format"],
    )

    config.redis_host = params["host"]
    config.redis_port = params["port"]
    config.redis_database = params["database"]
    config.redis_password = params["password"]
    config.redis_mode = params["redis_mode"]
    config.redis_key_expire_time = params["redis_key_expire_time"]
    config.redis_sentinel_instances = params["sentinel_instances"]
    config.redis_sentinel_password = params["sentinel_password"]
    config.redis_sentinel_socket_timeout = params["socket_timeout"]
    config.redis_sentinel_master_instance = params["master_instance"]
    config.redis_sentinel_master_password = params["master_password"]
    config.redis_sentinel_master_database = params["master_database"]

    config.timeout = params["timeout"]

    if params["broker"] == "sqs":
        if find_spec("boto3") is None:
            raise click.UsageError(
                "--broker=sqs needs the sqs extra: "
                "pip install 'remotecv[sqs]'"
            )
        try:
            sqs_broker = build_sqs_broker(
                params["key_id"],
                params["key_secret"],
                params["region"],
                params["timeout"],
                params["polling_interval"],
            )
        except ValueError as error:
            raise click.UsageError(
                "--key-id and --key-secret must be set together"
            ) from error
        config.broker_url, config.broker_transport_options = sqs_broker
    else:
        config.broker_url = _build_redis_broker_url()
        config.broker_transport_options = (
            _build_redis_broker_transport_options()
        )
    config.clear_image_metadata = params["clear_image_metadata"]
    config.max_image_pixels = params["max_image_pixels"]
    config.server_host = params["server_host"]
    config.server_port = params["server_port"]
    config.log_level = params["level"].upper()
    config.loader = import_module(params["loader"])
    config.loader_timeout = params["loader_timeout"]
    config.loader_max_body_size = params["loader_max_body_size"]
    config.loader_user_agent = params["loader_user_agent"]
    config.store = import_module(params["store"])

    config.metrics = params["metrics"]

    config.memcache_hosts = params["memcached_hosts"]

    config.extra_args = list(params["celery_commands"]) or ["worker"]

    config.error_handler = ErrorHandler(params["sentry_url"])

    import_modules()

    if params["with_healthcheck"]:
        start_http_server()

    start_celery_worker()


if __name__ == "__main__":
    main()
