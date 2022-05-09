import re
from urllib.request import unquote, urlopen


def load_sync(path):
    if not re.match(r"^https?", path):
        path = f"http://{path}"
    path = unquote(path)
    return urlopen(path).read()
