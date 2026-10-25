#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
from unittest import TestCase
from urllib import request

from remotecv import worker
from remotecv.healthcheck import HealthCheckHandler
from remotecv.utils import config


class HealthCheckTestCase(TestCase):
    def setUp(self):
        config.server_host = "127.0.0.1"
        config.server_port = 0
        self.httpd = worker.start_http_server()
        self.port = self.httpd.server_address[1]

    def tearDown(self):
        self.httpd.shutdown()

    def get(self, path="/", timeout=3):
        return request.urlopen(
            f"http://127.0.0.1:{self.port}{path}", timeout=timeout
        )

    def test_should_be_200_and_working(self):
        response = self.get()

        assert response.status == 200
        assert response.read().decode() == "WORKING"

    def test_should_not_expose_python_version(self):
        response = self.get()

        assert response.headers["Server"] == "remotecv"

    def test_should_answer_while_another_connection_is_idle(self):
        idle = socket.create_connection(("127.0.0.1", self.port))
        try:
            response = self.get()
            assert response.status == 200
        finally:
            idle.close()

    def test_should_close_idle_connection_after_timeout(self):
        with socket.create_connection(("127.0.0.1", self.port)) as idle:
            idle.settimeout(HealthCheckHandler.timeout + 1)
            assert idle.recv(1) == b""

    def test_should_bind_ipv6_address(self):
        config.server_host = "::1"
        httpd = worker.start_http_server()
        try:
            response = request.urlopen(
                f"http://[::1]:{httpd.server_address[1]}/", timeout=3
            )
            assert response.status == 200
        finally:
            httpd.shutdown()

    def test_should_accept_bracketed_ipv6_address(self):
        config.server_host = "[::1]"
        httpd = worker.start_http_server()
        try:
            response = request.urlopen(
                f"http://[::1]:{httpd.server_address[1]}/", timeout=3
            )
            assert response.status == 200
        finally:
            httpd.shutdown()

    def test_should_escape_control_characters_in_log(self):
        with self.assertLogs(level="INFO") as logs:
            with socket.create_connection(("127.0.0.1", self.port)) as sock:
                sock.sendall(b"GET /\x1b[31mred\x1b[0m HTTP/1.0\r\n\r\n")
                sock.recv(1024)

        assert "GET /\\x1b[31mred\\x1b[0m" in logs.output[0]
        assert "\x1b" not in logs.output[0]
