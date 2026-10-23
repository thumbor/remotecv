# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import os
from unittest import TestCase, mock

from remotecv import __version__
from remotecv.error_handler import ErrorHandler


class ErrorHandlerTestCase(TestCase):
    @mock.patch("remotecv.error_handler.sentry_sdk.init")
    def test_should_not_init_sentry_without_dsn(self, init_mock):
        ErrorHandler(None)
        init_mock.assert_not_called()

    @mock.patch(
        "remotecv.error_handler.get_default_release", return_value=None
    )
    @mock.patch("remotecv.error_handler.sentry_sdk.init")
    def test_should_init_sentry_with_dsn_and_release(self, init_mock, _):
        ErrorHandler("https://key@sentry.example.com/1")
        init_mock.assert_called_once_with(
            dsn="https://key@sentry.example.com/1",
            release=f"remotecv@{__version__}",
        )

    @mock.patch.dict(os.environ, {"SENTRY_RELEASE": "deploy-42"})
    @mock.patch("remotecv.error_handler.sentry_sdk.init")
    def test_should_keep_release_from_sentry_release_env(self, init_mock):
        ErrorHandler("https://key@sentry.example.com/1")
        init_mock.assert_called_once_with(
            dsn="https://key@sentry.example.com/1",
            release="deploy-42",
        )

    @mock.patch.dict(os.environ, {"CIRCLE_SHA1": "abc123"})
    @mock.patch("sentry_sdk.utils.get_git_revision", return_value=None)
    @mock.patch("remotecv.error_handler.sentry_sdk.init")
    def test_should_keep_release_detected_from_platform_env(
        self, init_mock, _
    ):
        os.environ.pop("SENTRY_RELEASE", None)
        ErrorHandler("https://key@sentry.example.com/1")
        init_mock.assert_called_once_with(
            dsn="https://key@sentry.example.com/1",
            release="abc123",
        )
