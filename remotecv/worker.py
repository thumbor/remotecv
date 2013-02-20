#!/usr/bin/python
# -*- coding: utf-8 -*-

# remote cv service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import sys
import argparse
import logging

from redis import Redis

from remotecv.utils import config

def import_module(name):
    module = __import__(name)
    if '.' in name:
        module = reduce(getattr, name.split('.')[1:], module)
    return module

def start_pyres_worker():
    from pyremotecv.unique_queue import UniqueWorker
    UniqueWorker.run(['Detect'], config.redis, timeout=config.timeout)

def start_celery_worker():
    from remotecv.celery_config import init_celery

    celery, detect_task = init_celery(config.key_id, config.key_secret, config.region, config.timeout)
    celery.start(config.extra_args)

def main(params=None):
    if params is None:
        params = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Runs RemoteCV.')

    conn_group = parser.add_argument_group('Worker Backend')
    conn_group.add_argument('-b', '--backend', default='pyres', choices=['pyres', 'celery'], help='Worker backend')

    conn_group = parser.add_argument_group('Pyres Connection Arguments')
    conn_group.add_argument('--host', default='localhost', help='Redis host')
    conn_group.add_argument('--port', default=6379, type=int, help='Redis port')
    conn_group.add_argument('--password', default=None, help='Redis password')

    conn_group = parser.add_argument_group('SQS Connection Arguments')
    conn_group.add_argument('--region', default='us-east-1', help='AWS SQS Region')
    conn_group.add_argument('--key_id', default='', help='AWS access key id')
    conn_group.add_argument('--key_secret', default='', help='AWS access key secret')

    other_group = parser.add_argument_group('Other arguments')
    other_group.add_argument('-l', '--level', default='debug', help='Logging level')
    other_group.add_argument('-o', '--loader', default='remotecv.http_loader', help='Loader used')
    other_group.add_argument('-t', '--timeout', default=None, type=int, help='Timeout in seconds for image detection')
    other_group.add_argument('args', nargs=argparse.REMAINDER)

    arguments = parser.parse_args(params)
    logging.basicConfig(level=getattr(logging, arguments.level.upper()))

    config.backend = arguments.backend
    config.redis_host = arguments.host
    config.redis_port = arguments.port
    config.redis_password = arguments.password
    config.redis = Redis(host=config.redis_host, port=config.redis_port, password=config.redis_password)

    config.region = arguments.region
    config.key_id = arguments.key_id
    config.key_secret = arguments.key_secret

    config.timeout = arguments.timeout
    config.loader = import_module(arguments.loader)

    config.extra_args = sys.argv[:1] + arguments.args

    if arguments.backend == 'pyres':
        start_pyres_worker()
    elif arguments.backend == 'celery':
        start_celery_worker()

if __name__ == "__main__":
    main()
