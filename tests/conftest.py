# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from unittest import mock

import pytest

from remotecv.utils import context


@pytest.fixture(autouse=True)
def reset_metrics():
    context.metrics = mock.Mock()
