# -*- coding: utf-8 -*-
#
# (c) 2016 Jonathan Bouzekri
#
# This file is part of the gMalt application
#
# MIT License : https://raw.githubusercontent.com/gmalt/fs-service/master/LICENSE

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "gmaltfileservice",
    version = read('VERSION'),
    author = "Jonathan Bouzekri",
    author_email = "jonathan.bouzekri@gmail.com",
    description = ("gMalt service using data from HGT files directly (not recommended for production)"),
    license = "MIT",
    keywords = "gis elevation altitude api webservice hgt",
    url = "http://github.com/gmalt/fileservice",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=(
        'celery', 'redis', 'weedi', 'gevent'
    ),
    extras_require={
        'test': ['flake8']
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    entry_points='''
        [console_scripts]
        gmalt-file-server = gmaltfileservice.app:run_server
        gmalt-file-worker = gmaltfileservice.app:run_worker

        [services]
        celery = gmaltfileservice.task:GmaltCelery
        server = gmaltfileservice.server:GmaltServer
    '''
)
