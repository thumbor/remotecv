import sys

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.utils import event_from_exception

from remotecv import __version__


class ErrorHandler:
    def __init__(self, sentry_url):
        self.sentry_client = None

        if not sentry_url:
            return

        kwargs = {
            "dsn": sentry_url,
            "integrations": [],
        }

        # Logging integration will create duplicates if below not ignored
        ignore_logger("thumbor")
        ignore_logger("tornado.access")

        sentry_sdk.init(**kwargs)
        self.install_handler()

    def install_handler(self):
        if not self.sentry_client:
            return
        old_hook = sys.excepthook

        def on_exception(exception_type, value, traceback):
            try:
                self.handle_error(exception_type, value, traceback)
            finally:
                old_hook(type, value, traceback)

        sys.excepthook = on_exception

    def handle_error(self, exception_type, value, traceback):
        exc_info = (exception_type, value, traceback)

        with sentry_sdk.push_scope() as scope:
            event, hint = event_from_exception(exc_info)
            scope.set_extra("remotecv-version", __version__)
            sentry_sdk.capture_event(event, hint=hint)
