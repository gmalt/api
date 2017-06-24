# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()


setup(
    name="gmaltapi",
    version=read('VERSION'),
    author="Jonathan Bouzekri",
    author_email="jonathan.bouzekri@gmail.com",
    description="gMalt server returning the altitude of a position",
    license="MIT",
    keywords="gis elevation altitude api webservice hgt",
    url="http://github.com/gmalt/fileservice",
    packages=find_packages(),
    long_description=read('README.rst'),
    install_requires=[
        'celery', 'redis', 'webob', 'gevent', 'configobj',
        'gmalthgtparser', 'routr', 'marshmallow'
    ],
    extras_require={
        'test': ['flake8', 'requests', 'pytest']
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
        gmalt-api-server = gmaltapi.admin:run_server
        gmalt-api-worker = gmaltapi.admin:run_worker

        [services]
        celery = gmaltapi.task:GmaltCelery
        server = gmaltapi.server:GmaltServer
    '''
)
