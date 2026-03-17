#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.error_handler import ErrorHandler


class ErrorHandlerTestCase(TestCase):
    def test_should_not_init_sentry_without_url(self):
        handler = ErrorHandler(None)
        expect(handler.sentry_client).to_be_null()

    @mock.patch("remotecv.error_handler.sentry_sdk")
    @mock.patch("remotecv.error_handler.ignore_logger")
    def test_should_init_sentry_with_url(
        self, ignore_logger_mock, sentry_mock
    ):
        ErrorHandler("https://sentry.example.com")

        sentry_mock.init.assert_called_once_with(
            dsn="https://sentry.example.com", integrations=[]
        )
        ignore_logger_mock.assert_any_call("thumbor")
        ignore_logger_mock.assert_any_call("tornado.access")

    def test_install_handler_does_nothing_without_sentry_client(self):
        handler = ErrorHandler(None)
        # Should be a no-op — no exception raised
        handler.install_handler()

    def test_install_handler_sets_excepthook_when_sentry_client_set(self):
        handler = ErrorHandler(None)
        handler.sentry_client = mock.Mock()

        original_hook = mock.Mock()
        with mock.patch("remotecv.error_handler.sys") as sys_mock:
            sys_mock.excepthook = original_hook
            handler.install_handler()
            expect(sys_mock.excepthook).Not.to_equal(original_hook)

    @mock.patch("remotecv.error_handler.sentry_sdk")
    @mock.patch("remotecv.error_handler.event_from_exception")
    def test_on_exception_closure_calls_handle_error(
        self, event_mock, sentry_mock
    ):
        handler = ErrorHandler(None)
        handler.sentry_client = mock.Mock()

        event_mock.return_value = ({}, {})
        scope_mock = mock.MagicMock()
        sentry_mock.push_scope.return_value.__enter__ = mock.Mock(
            return_value=scope_mock
        )
        sentry_mock.push_scope.return_value.__exit__ = mock.Mock(
            return_value=False
        )

        original_hook = mock.Mock()
        with mock.patch("remotecv.error_handler.sys") as sys_mock:
            sys_mock.excepthook = original_hook
            handler.install_handler()
            # Invoke the closure that install_handler registered as sys.excepthook
            new_hook = sys_mock.excepthook
            new_hook(ValueError, ValueError("oops"), None)

    @mock.patch("remotecv.error_handler.sentry_sdk")
    @mock.patch("remotecv.error_handler.event_from_exception")
    def test_handle_error_captures_event(self, event_mock, sentry_mock):
        handler = ErrorHandler(None)
        handler.sentry_client = mock.Mock()

        fake_event = {"type": "error"}
        fake_hint = {}
        event_mock.return_value = (fake_event, fake_hint)

        scope_mock = mock.MagicMock()
        sentry_mock.push_scope.return_value.__enter__ = mock.Mock(
            return_value=scope_mock
        )
        sentry_mock.push_scope.return_value.__exit__ = mock.Mock(
            return_value=False
        )

        handler.handle_error(ValueError, ValueError("oops"), None)

        sentry_mock.capture_event.assert_called_once_with(
            fake_event, hint=fake_hint
        )
        scope_mock.set_extra.assert_called_once()
