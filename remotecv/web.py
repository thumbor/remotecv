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
from pyres import ResQ
from itty import run_itty
from resweb import server as resweb_server

def main(params=None):
    if params is None:
        params = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Runs pyres web console.')

    conn_group = parser.add_argument_group('Connection arguments')
    conn_group.add_argument('--host', default='localhost', help='Binding host')
    conn_group.add_argument('--port', default=8080, type=int, help='Binding port')

    conn_group = parser.add_argument_group('Redis arguments')
    conn_group.add_argument('--redis-host', default='localhost', help='Redis host')
    conn_group.add_argument('--redis-port', default=6379, type=int, help='Redis port')
    conn_group.add_argument('--redis-password', default=None, help='Redis password')

    other_group = parser.add_argument_group('Other arguments')
    other_group.add_argument('-l', '--level', default='debug', help='Logging level')

    arguments = parser.parse_args(params)
    logging.basicConfig(level=getattr(logging, arguments.level.upper()))

    redis = Redis(host=arguments.redis_host, port=arguments.redis_port, password=arguments.redis_password)
    resweb_server.HOST = ResQ(redis)
    run_itty(host=arguments.host, port=arguments.port, server='wsgiref')

if __name__ == '__main__':
    main()
