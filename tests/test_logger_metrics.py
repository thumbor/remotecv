#!/usr/bin/python
# -*- coding: utf-8 -*-

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
