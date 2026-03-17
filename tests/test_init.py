# -*- coding: utf-8 -*-

import importlib
from importlib.metadata import PackageNotFoundError
from unittest import TestCase, mock

from preggy import expect


class VersionTestCase(TestCase):
    def test_version_fallback_when_package_not_found(self):
        import remotecv  # pylint: disable=import-outside-toplevel

        with mock.patch(
            "importlib.metadata.version",
            side_effect=PackageNotFoundError,
        ):
            importlib.reload(remotecv)
            expect(remotecv.__version__).to_equal("0+unknown")

        # Restore the real version for subsequent tests
        importlib.reload(remotecv)
