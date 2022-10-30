#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from json import loads

from aioredis import Redis
from aioredis.sentinel import Sentinel
from redis import RedisError


SINGLE_NODE = "single_node"
SENTINEL = "sentinel"


class Storage:
    def __init__(self, context):
        self.context = context
        self.redis_client = self.get_redis_client()

    async def get_detector_data(self, path):
        data = await self.redis_client.get(f"thumbor-detector-{path}")
        if data:
            return loads(data)
        return None

    def get_redis_client(self):
        redis_mode = str(self.context.config.REDIS_QUEUE_MODE).lower()

        if redis_mode == SINGLE_NODE:
            return self.__redis_single_node_client()
        if redis_mode == SENTINEL:
            return self.__redis_sentinel_client()

        raise RedisError(
            f"REDIS_QUEUE_MODE must be {SINGLE_NODE} or {SENTINEL}"
        )

    def __redis_single_node_client(self):
        return Redis(
            host=self.context.config.REDIS_QUEUE_SERVER_HOST,
            port=self.context.config.REDIS_QUEUE_SERVER_PORT,
            db=self.context.config.REDIS_QUEUE_SERVER_DB,
            password=self.context.config.REDIS_QUEUE_SERVER_PASSWORD,
        )

    def __redis_sentinel_client(self):

        instances_split = (
            self.context.config.REDIS_QUEUE_SENTINEL_INSTANCES.split(",")
        )
        instances = [
            tuple(instance.split(":")) for instance in instances_split
        ]

        if self.context.config.REDIS_QUEUE_SENTINEL_PASSWORD:
            sentinel_instance = Sentinel(
                instances,
                socket_timeout=self.context.config.REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT,
                sentinel_kwargs={
                    "password": self.context.config.REDIS_QUEUE_SENTINEL_PASSWORD
                },
            )
        else:
            sentinel_instance = Sentinel(
                instances,
                socket_timeout=self.context.config.REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT,
            )

        return sentinel_instance.master_for(
            self.context.config.REDIS_QUEUE_SENTINEL_MASTER_INSTANCE,
            socket_timeout=self.context.config.REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT,
            password=self.context.config.REDIS_QUEUE_SENTINEL_MASTER_PASSWORD,
            db=self.context.config.REDIS_QUEUE_SENTINEL_MASTER_DB,
        )
