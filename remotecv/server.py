#!/usr/bin/python
# -*- coding: utf-8 -*-

# remote cv service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import traceback
import sys
import argparse

import zmq

from remotecv.app import RemoteCvApp

def run_server(host, port):
    app = RemoteCvApp()
    context = zmq.Context()
    rep = context.socket(zmq.REP)
    rep.bind('tcp://%s:%s' % (host, port))
    while True:
        result = ''
        msg = rep.recv()
        try:
            result = app.process_request(msg)
        except:
            traceback.print_exc()
        rep.send(result)

def main(params=None):
    if params is None:
        params = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Runs RemoteCV.')

    conn_group = parser.add_argument_group('Connection arguments')
    conn_group.add_argument('-l', '--listen', default='*', help='IP address to listen')
    conn_group.add_argument('-p', '--port', default=13337, type=int, help='Port to listen')

    arguments = parser.parse_args(params)
    run_server(arguments.listen, arguments.port)


if __name__ == "__main__":
    main()
