# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Unit test of :mod:`gmaltapi.config` """

import pytest

from .conftest import ResetStingIO

import gmaltapi.config as config
import gmaltapi.app as app
import gmaltapi.handler
import gmaltapi.handlers.file


class TestGmaltServerConfigObj(object):
    def test_build_handler_spec(self):
        handler_spec = config \
            .GmaltServerConfigObj \
            ._build_handler_spec()
        opt1 = "option(celery, file, default=file)"
        opt2 = "option(file, celery, default=file)"
        assert handler_spec in [opt1, opt2]

    def test__init__wrong_type(self):
        conf_file = ResetStingIO("""
        [server]
        port = string
        """)

        with pytest.raises(ValueError) as exc:
            config.GmaltServerConfigObj(conf_file, app.App.spec)
        assert str(exc.value) == "'port' in ['server'] : the value " \
                                 "\"string\" is of the wrong type.\n"

    def test__init__wrong_handler(self):
        conf_file = ResetStingIO("""
        [server]
        handler = unknown
        """)

        with pytest.raises(ValueError) as exc:
            config.GmaltServerConfigObj(conf_file, app.App.spec)
        assert str(exc.value) == "'handler' in ['server'] : the value " \
                                 "\"unknown\" is unacceptable.\n"

    def test__init__file_handler_missing_folder(self):
        conf_file = ResetStingIO("""
        [server]
        handler = file
        """)

        with pytest.raises(ValueError) as exc:
            config.GmaltServerConfigObj(conf_file, app.App.spec)
        assert str(exc.value) == "'None' in ['handler'] : missing required\n"


def test_make_config_file_loader_default(filled_file_folder):
    conf_file = ResetStingIO("""
    [handler]
    folder = {}
    """.format(filled_file_folder))

    conf = config.GmaltServerConfigObj(conf_file, app.App.spec)
    assert conf['server']['host'] == 'localhost'
    assert conf['server']['port'] == 8088
    assert conf['server']['pool_size'] is None
    assert isinstance(conf['server']['handler'],
                      gmaltapi.handler.WSGIHandler)
    assert isinstance(conf['server']['handler'].alt_handler,
                      gmaltapi.handlers.file.Handler)
    assert conf['server']['handler'].alt_handler.folder == \
        str(filled_file_folder)
    assert conf['handler']['folder'] == str(filled_file_folder)


def test_make_config_file_loader(filled_file_folder):
    conf_file = ResetStingIO("""
    [server]
    host = 0.0.0.0
    port = 80
    pool_size = 100
    handler = file

    [handler]
    folder = {}
    """.format(filled_file_folder))

    conf = config.GmaltServerConfigObj(conf_file, app.App.spec)
    assert conf['server']['host'] == '0.0.0.0'
    assert conf['server']['port'] == 80
    assert conf['server']['pool_size'] == 100
    assert isinstance(conf['server']['handler'],
                      gmaltapi.handler.WSGIHandler)
    assert isinstance(conf['server']['handler'].alt_handler,
                      gmaltapi.handlers.file.Handler)
    assert conf['server']['handler'].alt_handler.folder == \
        str(filled_file_folder)
    assert conf['handler']['folder'] == str(filled_file_folder)
