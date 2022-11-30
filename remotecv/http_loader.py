import re

from urllib.request import unquote, urlopen
from urllib.parse import urlparse
from remotecv.timing import get_time, get_interval
from remotecv.utils import context


def load_sync(path):
    start_time = get_time()
    if not re.match(r"^https?", path):
        path = f"http://{path}"
    path = unquote(path)
    netloc = urlparse(path).netloc.replace(".", "_")
    response = urlopen(path)
    code = response.code
    result = response.read()

    context.metrics.incr("worker.original_image.response_bytes", len(result))
    context.metrics.timing(
        f"worker.original_image.fetch.{code}.{netloc}",
        get_interval(start_time, get_time()),
    )
    context.metrics.incr(
        f"worker.original_image.fetch.{code}.{netloc}",
    )
    context.metrics.incr(f"worker.original_image.status.{code}")
    context.metrics.incr(f"worker.original_image.status.{code}.{netloc}")

    return result
