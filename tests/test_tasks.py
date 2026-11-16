# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import numbers
from unittest import TestCase, mock

from remotecv.tasks import DetectTask
from remotecv.utils import config
from tests import read_fixture


class DetectTaskTestCase(TestCase):
    def test_should_run_detector_task(self):
        store_mock = mock.Mock()
        config.loader = mock.Mock(load_sync=read_fixture)
        config.store = store_mock
        config.store.ResultStore = mock.Mock(return_value=store_mock)
        DetectTask.perform("all", "group-smile-bw.jpg", "test-key")
        call = store_mock.store.call_args[0]

        key, img = call
        assert key == "test-key"
        assert len(img) > 20
        assert isinstance(img[0][0], numbers.Number)
        assert isinstance(img[0][1], numbers.Number)
        assert isinstance(img[0][2], numbers.Number)
        assert isinstance(img[0][3], numbers.Number)

    def test_should_not_log_credentials_or_query(self):
        config.loader = mock.Mock(
            load_sync=lambda _: read_fixture("one_face.jpg")
        )
        config.store = mock.Mock()
        config.store.ResultStore = mock.Mock(return_value=mock.Mock())

        with self.assertLogs("remotecv", level="INFO") as logs:
            DetectTask.perform(
                "face",
                "http://user:s3cret@images.example.com/a.jpg?sig=abc",
                "test-key",
            )

        assert (
            "Detecting face for http://images.example.com/a.jpg"
            in logs.output[0]
        )
        assert "s3cret" not in logs.output[0]
        assert "sig=abc" not in logs.output[0]
