# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Module testing the server with a `file` handler """

import pytest
import requests

from .conftest import ApiWebServer, ResetStingIO


@pytest.fixture
def file_server(folder):
    conf = ResetStingIO("""
    [server]
    handler = file

    [handler]
    folder = {}
    """.format(folder))
    return ApiWebServer(conf)


def test_get_altitude(file_server):
    with file_server:
        alt = requests.get(file_server.get_url(),
                           params={'lat': 0.9999, 'lng': 10.0001})
        assert alt.status_code == 200
        assert alt.json().get('alt') == 57
        alt = requests.get(file_server.get_url(),
                           params={'lat': 10.9999, 'lng': 10.0001})
        assert alt.status_code == 200
        assert alt.json().get('alt') is None
