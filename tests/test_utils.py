# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from unittest import TestCase
from urllib.parse import quote

from remotecv.utils import redact_url


class RedactUrlTestCase(TestCase):
    def test_should_keep_plain_url(self):
        url = "http://images.example.com/path/to/image.jpg"
        assert redact_url(url) == url

    def test_should_drop_userinfo(self):
        url = "https://user:s3cret@images.example.com/image.jpg"
        assert redact_url(url) == "https://images.example.com/image.jpg"

    def test_should_drop_query_and_fragment(self):
        url = "http://images.example.com/image.jpg?token=abc#frag"
        assert redact_url(url) == "http://images.example.com/image.jpg"

    def test_should_keep_port(self):
        url = "http://user:pass@images.example.com:8080/image.jpg?x=1"
        assert redact_url(url) == "http://images.example.com:8080/image.jpg"

    def test_should_keep_ipv6_host(self):
        url = "http://user:pass@[::1]:8080/image.jpg"
        assert redact_url(url) == "http://[::1]:8080/image.jpg"

    def test_should_tolerate_invalid_port(self):
        url = "http://user:pass@images.example.com:abc/image.jpg"
        assert redact_url(url) == "http://images.example.com/image.jpg"

    def test_should_keep_non_url_paths(self):
        assert redact_url("some/local/image.jpg") == "some/local/image.jpg"

    def test_should_keep_absolute_paths(self):
        assert redact_url("/tmp/image.jpg") == "/tmp/image.jpg"

    def test_should_redact_url_quoted_by_thumbor(self):
        url = quote("http://user:s3cret@images.example.com/a.jpg?sig=abc")
        assert redact_url(url) == "http://images.example.com/a.jpg"

    def test_should_redact_url_without_scheme(self):
        url = quote("user:s3cret@images.example.com/a.jpg?sig=abc")
        assert redact_url(url) == "images.example.com/a.jpg"

    def test_should_drop_query_from_path_without_host(self):
        assert redact_url("/tmp/image.jpg?token=abc") == "/tmp/image.jpg"

    def test_should_redact_protocol_relative_url(self):
        url = "//user:s3cret@images.example.com/a.jpg?sig=abc"
        assert redact_url(url) == "//images.example.com/a.jpg"

    def test_should_not_leak_password_after_encoded_slash(self):
        url = "http://user:ab%2Fcd@images.example.com/image.jpg"
        assert redact_url(url) == "<invalid url>"

    def test_should_redact_scheme_with_a_single_slash(self):
        url = "http:/user:s3cret@images.example.com/a.jpg?sig=abc"
        assert redact_url(url) == "http://images.example.com/a.jpg"

    def test_should_not_raise_on_invalid_ipv6_host(self):
        url = quote("http://user:s3cret@[::1/a.jpg?sig=abc")
        assert redact_url(url) == "<invalid url>"
