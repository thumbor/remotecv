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
from remotecv.error_handler import ErrorHandler

def import_module(name):
    module = __import__(name)
    if '.' in name:
        module = reduce(getattr, name.split('.')[1:], module)
    return module

def start_pyres_worker():
    from remotecv.unique_queue import UniqueWorker
    redis = Redis(host=config.redis_host, port=config.redis_port, db=config.redis_database, password=config.redis_password)
    def after_fork(job):
        config.error_handler.install_handler()
    worker = UniqueWorker(queues=['Detect'], server=redis, timeout=config.timeout, after_fork=after_fork)
    worker.work()

def start_celery_worker():
    from remotecv.celery_tasks import CeleryTasks

    celery_tasks = CeleryTasks(config.key_id, config.key_secret, config.region, config.timeout, config.polling_interval)
    celery_tasks.run_commands(config.extra_args, log_level=config.log_level)

def main(params=None):
    if params is None:
        params = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Runs RemoteCV.')

    conn_group = parser.add_argument_group('Worker Backend')
    conn_group.add_argument('-b', '--backend', default='pyres', choices=['pyres', 'celery'], help='Worker backend')

    conn_group = parser.add_argument_group('Pyres Connection Arguments')
    conn_group.add_argument('--host', default='localhost', help='Redis host')
    conn_group.add_argument('--port', default=6379, type=int, help='Redis port')
    conn_group.add_argument('--database', default=0, type=int, help='Redis database')
    conn_group.add_argument('--password', default=None, help='Redis password')

    conn_group = parser.add_argument_group('Celery/SQS Connection Arguments')
    conn_group.add_argument('--region', default='us-east-1', help='AWS SQS Region')
    conn_group.add_argument('--key_id', default='', help='AWS access key id')
    conn_group.add_argument('--key_secret', default='', help='AWS access key secret')
    conn_group.add_argument('--polling_interval', default=20, help='AWS polling interval')

    other_group = parser.add_argument_group('Other arguments')
    other_group.add_argument('-l', '--level', default='debug', help='Logging level')
    other_group.add_argument('-o', '--loader', default='remotecv.http_loader', help='Loader used')
    other_group.add_argument('-s', '--store', default='remotecv.result_store.redis_store', help='Loader used')
    other_group.add_argument('-t', '--timeout', default=None, type=int, help='Timeout in seconds for image detection')
    other_group.add_argument('--sentry_url', default=None, help='URL used to send errors to sentry')

    memcache_store_group = parser.add_argument_group('Memcache store arguments')
    memcache_store_group.add_argument('--memcache_hosts', default='localhost:11211', help='Comma separated list of memcache hosts')

    parser.add_argument('args', nargs=argparse.REMAINDER)

    arguments = parser.parse_args(params)
    logging.basicConfig(level=getattr(logging, arguments.level.upper()))

    config.backend = arguments.backend
    config.redis_host = arguments.host
    config.redis_port = arguments.port
    config.redis_database = arguments.database
    config.redis_password = arguments.password

    config.region = arguments.region
    config.key_id = arguments.key_id
    config.key_secret = arguments.key_secret
    config.polling_interval = arguments.polling_interval

    config.timeout = arguments.timeout
    config.log_level = arguments.level.upper()
    config.loader = import_module(arguments.loader)
    config.store = import_module(arguments.store)

    config.memcache_hosts = arguments.memcache_hosts

    config.extra_args = sys.argv[:1] + arguments.args

    config.error_handler = ErrorHandler(arguments.sentry_url)

    if arguments.backend == 'pyres':
        start_pyres_worker()
    elif arguments.backend == 'celery':
        start_celery_worker()

if __name__ == "__main__":
    main()
