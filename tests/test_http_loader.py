#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv import http_loader
from remotecv.utils import context


class HttpLoaderTestCase(TestCase):
    def setUp(self):
        context.metrics = mock.Mock()

    def _make_response(self, body=b"image data", code=200):
        response = mock.Mock()
        response.code = code
        response.read.return_value = body
        return response

    @mock.patch("remotecv.http_loader.urlopen")
    def test_load_sync_with_http_url(self, urlopen_mock):
        urlopen_mock.return_value = self._make_response(b"img", 200)

        result = http_loader.load_sync("http://example.com/image.jpg")

        expect(result).to_equal(b"img")
        urlopen_mock.assert_called_once_with("http://example.com/image.jpg")

    @mock.patch("remotecv.http_loader.urlopen")
    def test_load_sync_prepends_http_when_missing(self, urlopen_mock):
        urlopen_mock.return_value = self._make_response(b"img", 200)

        http_loader.load_sync("example.com/image.jpg")

        urlopen_mock.assert_called_once_with("http://example.com/image.jpg")

    @mock.patch("remotecv.http_loader.urlopen")
    def test_load_sync_sends_metrics(self, urlopen_mock):
        urlopen_mock.return_value = self._make_response(b"data", 200)

        http_loader.load_sync("http://example.com/image.jpg")

        context.metrics.incr.assert_any_call(
            "worker.original_image.response_bytes", 4
        )
        context.metrics.timing.assert_called_once()
