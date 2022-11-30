# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022, globo.com <thumbor@g.globo>

import time


def get_time():
    return time.perf_counter_ns()


def get_interval(start, end):
    return nano_to_ms(end - start)


def nano_to_ms(ns_time):
    return ns_time / 1e6
