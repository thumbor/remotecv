# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from unittest import TestCase

from remotecv.metrics.logger_metrics import Metrics
from remotecv.utils import config


class LoggerMetricsTestCase(TestCase):
    def setUp(self):
        self.metrics = Metrics(config)

    def test_incr(self):
        # Should not raise; just logs
        self.metrics.incr("some.metric")
        self.metrics.incr("some.metric", value=5)

    def test_timing(self):
        # Should not raise; just logs
        self.metrics.timing("some.metric", 42.0)
