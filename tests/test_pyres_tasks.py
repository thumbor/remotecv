#!/usr/bin/python
# -*- coding: utf-8 -*-

import mock
from preggy import expect
from unittest import TestCase
from tests import read_fixture

from remotecv.pyres_tasks import DetectTask
from remotecv.utils import config


class DetectTaskTestCase(TestCase):

    def test_should_run_detector_task(self):
        store_mock = mock.Mock()
        config.loader = mock.Mock(load_sync=read_fixture)
        config.store = store_mock
        config.store.ResultStore = mock.Mock(return_value=store_mock)
        DetectTask.perform('all', 'multiple_faces_bw.jpg', 'test-key')
        call = store_mock.store.call_args[0]
        expect(call[0]).to_equal('test-key')
        expect(call[1]).to_be_greater_than(20)
        expect(call[1][0][0]).to_be_numeric()
        expect(call[1][0][1]).to_be_numeric()
        expect(call[1][0][2]).to_be_numeric()
        expect(call[1][0][3]).to_be_numeric()
