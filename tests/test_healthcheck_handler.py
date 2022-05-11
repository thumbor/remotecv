#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase
from urllib import request

from preggy import expect

from remotecv import worker
from remotecv.utils import config


class HealthCheckTestCase(TestCase):
    def test_should_be_200_and_working(self):
        config.server_port = 8888

        worker.start_http_server()
        response = request.urlopen(f"http://localhost:{config.server_port}")

        expect(response.status).to_equal(200)
        expect(response.read().decode()).to_equal("WORKING")
