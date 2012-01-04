#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from setuptools import setup, Extension
from remotecv import __version__

setup(
    name = 'remotecv',
    version = __version__,
    description = "remotecv is an OpenCV server for facial and feature recognition",
    long_description = """
remotecv is an OpenCV server for facial and feature recognition
""",
    keywords = 'imaging face detection feature opencv',
    author = 'globo.com',
    author_email = 'timehome@corp.globo.com',
    url = 'https://github.com/globocom/remotecv/wiki',
    license = 'MIT',
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: MacOS',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.6',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Multimedia :: Graphics :: Presentation'
    ],
    packages = ['remotecv'],
    package_dir = {"remotecv": "remotecv"},

    install_requires=[
        "pyzmq>=2.1.11,<2.2.0",
        "bson>=0.3.3,<0.4.0"
    ],

    entry_points = {
        'console_scripts': [
            'remotecv = remotecv.server:main'
        ],
    }
)
