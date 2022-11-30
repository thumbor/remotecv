# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022, globo.com <thumbor@g.globo>


class BaseMetrics:
    def __init__(self, config):
        self.config = config

    def initialize(self):
        pass

    def incr(self, metricname, value=1):
        raise NotImplementedError()

    def timing(self, metricname, value):
        raise NotImplementedError()
