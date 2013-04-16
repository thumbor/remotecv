import pkgutil
import pkg_resources
import sys

from remotecv.utils import config

class ErrorHandler:
    def __init__(self, sentry_url):
        self.sentry_client = None

        if not sentry_url:
            return

        from raven import Client
        self.sentry_client = Client(sentry_url)
        self.extra_data = {
            'modules': self.get_modules()
        }
        self.install_handler()

    def get_modules(self):
        resolved = {}
        modules = [mod[1] for mod in tuple(pkgutil.iter_modules())]
        for module in modules:
            try:
                res_mod = pkg_resources.get_distribution(module)
                if res_mod is not None:
                    resolved[module] = res_mod.version
            except pkg_resources.DistributionNotFound:
                pass

        return resolved

    def install_handler(self):
        if not self.sentry_client:
            return
        old_hook = sys.excepthook
        def on_exception(type, value, traceback):
            try:
                self.sentry_client.captureException((type, value, traceback), data=self.extra_data)
            finally:
                old_hook(type, value, traceback)
        sys.excepthook = on_exception
