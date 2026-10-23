#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.pyres_tasks import DetectTask
from remotecv.utils import config, context
from tests import read_fixture


class DetectTaskTestCase(TestCase):
    def test_should_run_detector_task(self):
        store_mock = mock.Mock()
        config.loader = mock.Mock(load_sync=read_fixture)
        config.store = store_mock
        config.store.ResultStore = mock.Mock(return_value=store_mock)
        context.metrics = mock.Mock()
        DetectTask.perform("all", "group-smile-bw.jpg", "test-key")
        call = store_mock.store.call_args[0]

        key, img = call
        expect(key).to_equal("test-key")
        expect(len(img)).to_be_greater_than(20)
        expect(img[0][0]).to_be_numeric()
        expect(img[0][1]).to_be_numeric()
        expect(img[0][2]).to_be_numeric()
        expect(img[0][3]).to_be_numeric()

    def test_should_not_log_credentials_or_query(self):
        config.loader = mock.Mock(
            load_sync=lambda _: read_fixture("one_face.jpg")
        )
        config.store = mock.Mock()
        config.store.ResultStore = mock.Mock(return_value=mock.Mock())
        context.metrics = mock.Mock()

        with self.assertLogs("remotecv", level="INFO") as logs:
            DetectTask.perform(
                "face",
                "http://user:s3cret@images.example.com/a.jpg?sig=abc",
                "test-key",
            )

        expect(logs.output[0]).to_include(
            "Detecting face for http://images.example.com/a.jpg"
        )
        expect(logs.output[0]).Not.to_include("s3cret")
        expect(logs.output[0]).Not.to_include("sig=abc")
