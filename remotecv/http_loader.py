import re
from http.client import InvalidURL
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, build_opener, unquote

from remotecv.timing import get_interval, get_time
from remotecv.utils import config, context, redact_url

DEFAULT_TIMEOUT = 20.0
DEFAULT_MAX_BODY_SIZE = 0
ALLOWED_SCHEMES = ("http", "https")


class BodyTooLargeError(Exception):
    pass


class HttpOnlyRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self, req, fp, code, msg, headers, newurl
    ):  # pylint: disable=too-many-positional-arguments
        if urlparse(newurl).scheme not in ALLOWED_SCHEMES:
            raise URLError(f"redirect to unsupported scheme: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def declared_length(response):
    try:
        return int(response.headers.get("Content-Length", ""))
    except ValueError:
        return None


def read_body(response, max_body_size):
    if not max_body_size:
        return response.read()

    content_length = declared_length(response)
    if content_length is not None and content_length > max_body_size:
        raise BodyTooLargeError(
            f"Content-Length {content_length} exceeds {max_body_size} bytes"
        )

    body = response.read(max_body_size + 1)
    if len(body) > max_body_size:
        raise BodyTooLargeError(f"body exceeds {max_body_size} bytes")

    return body


def load_sync(path):
    start_time = get_time()
    if not re.match(r"^https?", path):
        path = f"http://{path}"
    path = unquote(path)
    parsed = urlparse(path)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise URLError(f"unsupported scheme: {parsed.scheme}")
    host = (parsed.hostname or "").replace(".", "_").replace(":", "_")

    opener = build_opener(HttpOnlyRedirectHandler)
    try:
        response = opener.open(
            path, timeout=getattr(config, "loader_timeout", DEFAULT_TIMEOUT)
        )
    except (InvalidURL, ValueError):
        # urllib echoes the URL, userinfo and query included, in these.
        raise ValueError(f"invalid image URL {redact_url(path)}") from None
    with response:
        code = response.code
        result = read_body(
            response,
            getattr(config, "loader_max_body_size", DEFAULT_MAX_BODY_SIZE),
        )

    context.metrics.incr("worker.original_image.response_bytes", len(result))
    context.metrics.timing(
        f"worker.original_image.fetch.{code}.{host}",
        get_interval(start_time, get_time()),
    )
    context.metrics.incr(
        f"worker.original_image.fetch.{code}.{host}",
    )
    context.metrics.incr(f"worker.original_image.status.{code}")
    context.metrics.incr(f"worker.original_image.status.{code}.{host}")

    return result
