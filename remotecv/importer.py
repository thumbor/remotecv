# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022, globo.com <thumbor@g.globo>

from importlib import import_module


class Importer:
    @classmethod
    def import_class(cls, class_name, conf_value):
        module = import_module(conf_value)
        return getattr(module, class_name)
