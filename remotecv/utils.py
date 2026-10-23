# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import logging
import re
from urllib.parse import unquote, urlsplit, urlunsplit

from redis import Redis, Sentinel

from remotecv.timing import get_interval, get_time


class Config:
    pass


class Context:
    pass


logger = logging.getLogger("remotecv")  # pylint: disable=invalid-name
config = Config()  # pylint: disable=invalid-name
context = Context()

SINGLE_NODE = "single_node"
SENTINEL = "sentinel"

SCHEME = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.-]*):/{1,2}")


def redact_url(url):
    # thumbor enqueues the image URL percent-encoded and usually without a
    # scheme, so normalize it the way http_loader.load_sync does first.
    # A single slash after the scheme would leave the userinfo in the path.
    url, schemes = SCHEME.subn(r"\1://", unquote(url))
    has_authority = bool(schemes) or url.startswith("//")
    try:
        parts = urlsplit(url if has_authority else f"//{url}")
    except ValueError:
        # Callers format this into log lines and error messages, which must
        # not fail because the URL they describe is malformed.
        return "<invalid url>"

    netloc = parts.hostname or ""
    if ":" in netloc:
        netloc = f"[{netloc}]"
    try:
        if parts.port:
            netloc = f"{netloc}:{parts.port}"
    except ValueError:
        # An encoded '/' in a password unquotes into the path, and urllib
        # rejects the non-numeric port that results, so the URL is invalid.
        if "@" in parts.path:
            return "<invalid url>"

    redacted = urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    return redacted if has_authority else redacted.removeprefix("//")


def redis_client():
    start_time = get_time()
    if config.redis_mode == SINGLE_NODE:
        client = __redis_single_node_client()
    elif config.redis_mode == SENTINEL:
        client = __redis_sentinel_client()
    else:
        raise AttributeError(
            f"redis-mode must be either {SINGLE_NODE} or {SENTINEL}"
        )

    context.metrics.timing(
        "worker.redis_connection.time",
        get_interval(start_time, get_time()),
    )

    return client


def __redis_sentinel_client():
    instances_split = config.redis_sentinel_instances.split(",")
    instances = [instance.split(":") for instance in instances_split]

    if config.redis_sentinel_password:
        sentinel_instance = Sentinel(
            instances,
            socket_timeout=config.redis_sentinel_socket_timeout,
            sentinel_kwargs={"password": config.redis_sentinel_password},
        )
    else:
        sentinel_instance = Sentinel(
            instances,
            socket_timeout=config.redis_sentinel_socket_timeout,
        )

    return sentinel_instance.master_for(
        config.redis_sentinel_master_instance,
        socket_timeout=config.redis_sentinel_socket_timeout,
        password=config.redis_sentinel_master_password,
        db=config.redis_sentinel_master_database,
    )


def __redis_single_node_client():
    if config.redis_password:
        return Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_database,
            password=config.redis_password,
        )

    return Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_database,
    )
