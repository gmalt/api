# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Module testing the WSGI handler standard implementation """

import pytest
import requests

from .conftest import ApiWebServer, ResetStingIO


@pytest.fixture
def generic_server(folder):
    conf = ResetStingIO("""
    [server]
    handler = file

    [handler]
    folder = {}
    """.format(folder))
    return ApiWebServer(conf)


def test_no_route(generic_server):
    with generic_server:
        res = requests.get(generic_server.get_base_url() + '/unknown_route')
        assert res.status_code == 404
        assert res.json().get('code') == 404
        assert res.json().get('message') == 'The resource could not be' \
                                            ' found. Use GET /altitude' \
                                            ' instead.'
        assert res.json().get('title') == 'Not Found'


def test_bad_request(generic_server):
    with generic_server:
        res = requests.get(generic_server.get_url())
        assert res.status_code == 400
        assert res.json().get('lat')[0] == 'Missing data for required field.'
        assert res.json().get('lng')[0] == 'Missing data for required field.'

        res = requests.get(generic_server.get_url(), params={'lat': 0.999})
        assert res.status_code == 400
        assert 'lat' not in res.json()
        assert res.json().get('lng')[0] == 'Missing data for required field.'

        res = requests.get(generic_server.get_url(), params={'lat': 'ABC'})
        assert res.status_code == 400
        assert res.json().get('lat')[0] == 'Not a valid number.'
        assert res.json().get('lng')[0] == 'Missing data for required field.'

        res = requests.get(generic_server.get_url(), params={'lng': 0.999})
        assert res.status_code == 400
        assert res.json().get('lat')[0] == 'Missing data for required field.'
        assert 'lng' not in res.json()

        res = requests.get(generic_server.get_url(), params={'lng': 'ABC'})
        assert res.status_code == 400
        assert res.json().get('lat')[0] == 'Missing data for required field.'
        assert res.json().get('lng')[0] == 'Not a valid number.'

        res = requests.get(generic_server.get_url(), params={'lat': 'ABC',
                                                             'lng': 'ABC'})
        assert res.status_code == 400
        assert res.json().get('lat')[0] == 'Not a valid number.'
        assert res.json().get('lng')[0] == 'Not a valid number.'

        res = requests.get(generic_server.get_url(), params={'lat': None,
                                                             'lng': None})
        assert res.status_code == 400
        assert res.json().get('lat')[0] == 'Missing data for required field.'
        assert res.json().get('lng')[0] == 'Missing data for required field.'


def test_options_altitude(generic_server):
    with generic_server:
        res = requests.options(generic_server.get_url())
        assert res.status_code == 200
        assert res.text == ''
