import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.utils import get_default_release

from remotecv import __version__


class ErrorHandler:
    def __init__(self, sentry_url):
        if not sentry_url:
            return

        # Logging integration will create duplicates if below not ignored
        ignore_logger("thumbor")
        ignore_logger("tornado.access")

        release = get_default_release() or f"remotecv@{__version__}"
        sentry_sdk.init(dsn=sentry_url, release=release)
