# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import importlib
from importlib.metadata import PackageNotFoundError
from unittest import TestCase, mock


class VersionTestCase(TestCase):
    def test_version_fallback_when_package_not_found(self):
        import remotecv  # pylint: disable=import-outside-toplevel

        with mock.patch(
            "importlib.metadata.version",
            side_effect=PackageNotFoundError,
        ):
            importlib.reload(remotecv)
            assert remotecv.__version__ == "0+unknown"

        # Restore the real version for subsequent tests
        importlib.reload(remotecv)
