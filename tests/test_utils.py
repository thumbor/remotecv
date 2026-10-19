from unittest import TestCase
from urllib.parse import quote

from preggy import expect

from remotecv.utils import redact_url


class RedactUrlTestCase(TestCase):
    def test_should_keep_plain_url(self):
        url = "http://images.example.com/path/to/image.jpg"
        expect(redact_url(url)).to_equal(url)

    def test_should_drop_userinfo(self):
        url = "https://user:s3cret@images.example.com/image.jpg"
        expect(redact_url(url)).to_equal(
            "https://images.example.com/image.jpg"
        )

    def test_should_drop_query_and_fragment(self):
        url = "http://images.example.com/image.jpg?token=abc#frag"
        expect(redact_url(url)).to_equal("http://images.example.com/image.jpg")

    def test_should_keep_port(self):
        url = "http://user:pass@images.example.com:8080/image.jpg?x=1"
        expect(redact_url(url)).to_equal(
            "http://images.example.com:8080/image.jpg"
        )

    def test_should_keep_ipv6_host(self):
        url = "http://user:pass@[::1]:8080/image.jpg"
        expect(redact_url(url)).to_equal("http://[::1]:8080/image.jpg")

    def test_should_tolerate_invalid_port(self):
        url = "http://user:pass@images.example.com:abc/image.jpg"
        expect(redact_url(url)).to_equal("http://images.example.com/image.jpg")

    def test_should_keep_non_url_paths(self):
        expect(redact_url("some/local/image.jpg")).to_equal(
            "some/local/image.jpg"
        )

    def test_should_keep_absolute_paths(self):
        expect(redact_url("/tmp/image.jpg")).to_equal("/tmp/image.jpg")

    def test_should_redact_url_quoted_by_thumbor(self):
        url = quote("http://user:s3cret@images.example.com/a.jpg?sig=abc")
        expect(redact_url(url)).to_equal("http://images.example.com/a.jpg")

    def test_should_redact_url_without_scheme(self):
        url = quote("user:s3cret@images.example.com/a.jpg?sig=abc")
        expect(redact_url(url)).to_equal("images.example.com/a.jpg")

    def test_should_drop_query_from_path_without_host(self):
        expect(redact_url("/tmp/image.jpg?token=abc")).to_equal(
            "/tmp/image.jpg"
        )

    def test_should_redact_protocol_relative_url(self):
        url = "//user:s3cret@images.example.com/a.jpg?sig=abc"
        expect(redact_url(url)).to_equal("//images.example.com/a.jpg")

    def test_should_not_leak_password_after_encoded_slash(self):
        url = "http://user:ab%2Fcd@images.example.com/image.jpg"
        expect(redact_url(url)).to_equal("<invalid url>")

    def test_should_redact_scheme_with_a_single_slash(self):
        url = "http:/user:s3cret@images.example.com/a.jpg?sig=abc"
        expect(redact_url(url)).to_equal("http://images.example.com/a.jpg")

    def test_should_not_raise_on_invalid_ipv6_host(self):
        url = quote("http://user:s3cret@[::1/a.jpg?sig=abc")
        expect(redact_url(url)).to_equal("<invalid url>")
