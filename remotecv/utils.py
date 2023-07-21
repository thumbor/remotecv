#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import logging

from redis import Redis, Sentinel

from remotecv.timing import get_time, get_interval


class Config:
    pass


class Context:
    pass


logger = logging.getLogger("remotecv")  # pylint: disable=invalid-name
config = Config()  # pylint: disable=invalid-name
context = Context()

SINGLE_NODE = "single_node"
SENTINEL = "sentinel"


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
