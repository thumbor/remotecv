#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from preggy import expect

from remotecv.pyres_tasks import DetectTask
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
        expect(key).to_equal("test-key")
        expect(len(img)).to_be_greater_than(20)
        expect(img[0][0]).to_be_numeric()
        expect(img[0][1]).to_be_numeric()
        expect(img[0][2]).to_be_numeric()
        expect(img[0][3]).to_be_numeric()
