import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest import TestCase, mock
from urllib.error import URLError

from preggy import expect

from remotecv.http_loader import BodyTooLargeError, load_sync
from remotecv.utils import config, context

SMALL_BODY = b"image-bytes"
LARGE_BODY = b"x" * 2048


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/small":
            self.respond(SMALL_BODY)
        elif self.path == "/large":
            self.respond(LARGE_BODY)
        elif self.path == "/large-no-length":
            self.respond(LARGE_BODY, with_length=False)
        elif self.path == "/small-bad-length":
            self.respond(SMALL_BODY, length="abc")
        elif self.path == "/large-bad-length":
            self.respond(LARGE_BODY, length="abc")
        elif self.path == "/redirect-http":
            self.redirect(f"http://127.0.0.1:{self.server.server_port}/small")
        elif self.path == "/redirect-ftp":
            self.redirect("ftp://127.0.0.1/small")
        elif self.path == "/slow":
            time.sleep(2)
        else:
            self.send_error(404)

    def respond(self, body, with_length=True, length=None):
        self.send_response(200)
        if with_length:
            self.send_header("Content-Length", length or str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, format, *args):  # pylint: disable=redefined-builtin
        pass


class HttpLoaderTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        cls.httpd.daemon_threads = True
        Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base_url = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        context.metrics = mock.Mock()
        config.loader_timeout = 5.0
        config.loader_max_body_size = 0

    def test_should_load_image(self):
        expect(load_sync(f"{self.base_url}/small")).to_equal(SMALL_BODY)

    def test_should_prepend_http_when_scheme_is_missing(self):
        url = f"{self.base_url}/small"[len("http://") :]
        expect(load_sync(url)).to_equal(SMALL_BODY)

    def test_should_follow_http_redirect(self):
        expect(load_sync(f"{self.base_url}/redirect-http")).to_equal(
            SMALL_BODY
        )

    def test_should_refuse_redirect_to_other_scheme(self):
        with self.assertRaisesRegex(
            URLError, "redirect to unsupported scheme"
        ):
            load_sync(f"{self.base_url}/redirect-ftp")

    def test_should_refuse_non_http_scheme(self):
        with self.assertRaisesRegex(URLError, "unsupported scheme: httpx"):
            load_sync("httpx://127.0.0.1/small")

    def test_should_allow_body_within_limit(self):
        config.loader_max_body_size = len(LARGE_BODY)
        expect(load_sync(f"{self.base_url}/large")).to_equal(LARGE_BODY)

    def test_should_refuse_body_by_content_length(self):
        config.loader_max_body_size = len(LARGE_BODY) - 1
        with expect.error_to_happen(BodyTooLargeError):
            load_sync(f"{self.base_url}/large")

    def test_should_refuse_body_without_content_length(self):
        config.loader_max_body_size = len(LARGE_BODY) - 1
        with expect.error_to_happen(BodyTooLargeError):
            load_sync(f"{self.base_url}/large-no-length")

    def test_should_ignore_malformed_content_length(self):
        config.loader_max_body_size = len(LARGE_BODY) - 1
        expect(load_sync(f"{self.base_url}/small-bad-length")).to_equal(
            SMALL_BODY
        )
        with expect.error_to_happen(BodyTooLargeError):
            load_sync(f"{self.base_url}/large-bad-length")

    def test_should_time_out(self):
        config.loader_timeout = 0.2
        with expect.error_to_happen((URLError, TimeoutError)):
            load_sync(f"{self.base_url}/slow")

    def test_should_send_metrics(self):
        load_sync(f"{self.base_url}/small")
        context.metrics.incr.assert_any_call(
            "worker.original_image.response_bytes", len(SMALL_BODY)
        )
        context.metrics.incr.assert_any_call(
            "worker.original_image.status.200"
        )


class HttpLoaderMetricsTestCase(TestCase):
    def setUp(self):
        context.metrics = mock.Mock()

    @mock.patch("remotecv.http_loader.build_opener")
    def test_should_not_put_credentials_in_metric_names(
        self, build_opener_mock
    ):
        build_opener_mock.return_value.open.return_value = mock.MagicMock(
            code=200, read=mock.Mock(return_value=b"image")
        )

        load_sync("http://user:s3cret@images.example.com:8080/image.jpg")

        names = [
            call.args[0] for call in context.metrics.incr.call_args_list
        ] + [call.args[0] for call in context.metrics.timing.call_args_list]
        expect(names).to_include(
            "worker.original_image.fetch.200.images_example_com"
        )
        for name in names:
            expect(name).Not.to_include("s3cret")
            expect(name).Not.to_include("8080")

    @mock.patch("remotecv.http_loader.build_opener")
    def test_should_not_put_colons_of_ipv6_host_in_metric_names(
        self, build_opener_mock
    ):
        build_opener_mock.return_value.open.return_value = mock.MagicMock(
            code=200, read=mock.Mock(return_value=b"image")
        )

        load_sync("http://[::1]:8080/image.jpg")

        context.metrics.incr.assert_any_call(
            "worker.original_image.fetch.200.__1"
        )

    def test_should_not_put_credentials_in_invalid_url_error(self):
        for url, redacted in [
            (
                "http://user:s3cret@images.example.com/a.jpg?sig=abc",
                "http://images.example.com/a.jpg",
            ),
            (
                "http://images.example.com/a%20b.jpg?sig=abc",
                "http://images.example.com/a b.jpg",
            ),
        ]:
            with self.assertRaises(ValueError) as error:
                load_sync(url)

            expect(str(error.exception)).to_equal(
                f"invalid image URL {redacted}"
            )
            expect(error.exception.__suppress_context__).to_be_true()

    def test_should_refuse_scheme_less_url_without_echoing_it(self):
        with self.assertRaises(URLError) as error:
            load_sync("https-images.example.com/a.jpg?sig=abc")

        expect(str(error.exception)).Not.to_include("sig")

    def test_should_not_leak_password_after_encoded_slash_in_error(self):
        with self.assertRaises(ValueError) as error:
            load_sync("http://user:ab%2Fcd@images.example.com/image.jpg")

        expect(str(error.exception)).to_equal(
            "invalid image URL <invalid url>"
        )
