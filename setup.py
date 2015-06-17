#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from setuptools import setup, find_packages
from remotecv import __version__

tests_require = [
    "pyvows",
    "preggy",
    "coverage",
    "thumbor",
    "numpy"
]

setup(
    name='remotecv',
    version=__version__,
    description="remotecv is an OpenCV worker for facial and feature recognition",
    long_description="""
remotecv is an OpenCV worker for facial and feature recognition
""",
    keywords='imaging face detection feature opencv',
    author='globo.com',
    author_email='timehome@corp.globo.com',
    url='https://github.com/globocom/remotecv/wiki',
    license='MIT',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Operating System :: MacOS',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.6',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                 'Topic :: Multimedia :: Graphics :: Presentation'],
    packages=find_packages(),
    package_data={
        '': ['*.xml'],
    },

    extras_require={
        'tests': tests_require,
    },

    install_requires=[
        "argparse>=1.2.1,<1.3.0",
        "pyres>=1.2,<1.3",
        "Pillow>=2.3.0,<3.0.0",
    ],

    entry_points={
        'console_scripts': [
            'remotecv = remotecv.worker:main',
            'remotecv-web = remotecv.web:main'
        ],
    }
)
