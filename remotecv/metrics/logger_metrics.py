# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022, globo.com <thumbor@g.globo>

from remotecv.metrics import BaseMetrics
from remotecv.utils import logger


class Metrics(BaseMetrics):
    def incr(self, metricname, value=1):
        logger.debug("METRICS: inc: %s:%d", metricname, value)

    def timing(self, metricname, value):
        logger.debug("METRICS: timing: %s:%d", metricname, value)
