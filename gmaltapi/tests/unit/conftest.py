# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Module providing configuration for pytest to run unit tests """

import pytest

from .. import ResetStingIO  # noqa


@pytest.fixture()
def empty_file_folder(tmpdir):
    return tmpdir.mkdir("gmaltunit")


@pytest.fixture()
def filled_file_folder(tmpdir):
    folder = tmpdir.mkdir("gmaltunit")
    folder.join("file.hgt").write('random content')
    return folder


class MockHandler(object):
    def __init__(self):
        self.lat = None
        self.lng = None

    def get_altitude(self, lat, lng):
        self.lat = lat
        self.lng = lng
        return 57


@pytest.fixture()
def mock_handler():
    return MockHandler()


class MockResponse(object):
    def __init__(self):
        self.status = None
        self.response_headers = None

    def __call__(self, status, response_headers):
        self.status = status
        self.response_headers = response_headers


@pytest.fixture()
def mock_response():
    return MockResponse()
