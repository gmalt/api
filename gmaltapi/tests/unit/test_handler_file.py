# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Unit test of :mod:`gmaltapi.handlers.file` """

import os

import gmalthgtparser
import pytest

from gmaltapi.handlers.file import Handler


@pytest.fixture()
def empty_file_folder(tmpdir):
    return tmpdir.mkdir("gmaltunit")


@pytest.fixture()
def filled_file_folder(tmpdir):
    folder = tmpdir.mkdir("gmaltunit")
    folder.join("file.hgt").write('random content')
    return folder


def test_hgt_filename_from_coordinates():
    result = Handler._hgt_filename_from_coordinates((0, 0))
    assert result == 'N00E000.hgt'

    result = Handler._hgt_filename_from_coordinates((-1, -1))
    assert result == 'S01W001.hgt'

    result = Handler._hgt_filename_from_coordinates((-45, -128))
    assert result == 'S45W128.hgt'

    result = Handler._hgt_filename_from_coordinates((1, 1))
    assert result == 'N01E001.hgt'

    result = Handler._hgt_filename_from_coordinates((45, 128))
    assert result == 'N45E128.hgt'


def test__init__unknown_folder(empty_file_folder):
    unknown_folder = empty_file_folder.join('unknown')
    with pytest.raises(Exception) as e:
        Handler(str(unknown_folder))
    assert str(e.value) == 'folder {} does not exists or is not a ' \
                           'directory'.format(str(unknown_folder))


def test__init__empty_folder(empty_file_folder):
    with pytest.raises(Exception) as e:
        Handler(str(empty_file_folder))
    assert str(e.value) == 'folder {} does not contain any HGT ' \
                           'file'.format(str(empty_file_folder))


def test__init__valid_folder(filled_file_folder):
    try:
        hd = Handler(str(filled_file_folder))
        assert hd.folder == str(filled_file_folder)
    except Exception:
        pytest.fail("_validate_folder should not have raised exception")


class MockHgtParser(object):
    def __init__(self, file_):
        self.file = file_
        self.pos = None
        self.enter_called = False
        self.exit_called = False

    def __enter__(self):
        self.enter_called = True
        return self

    def get_elevation(self, pos):
        self.pos = pos
        return 1, 2, 57

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_called = True

    def __str__(self):
        return 'MockHgtParser(file={file}, pos={pos}, ' \
               'enter_called={enter_called}, ' \
               'exit_called={exit_called})'.format(**self.__dict__)


def test_get_altitude_hgt_file_exist(filled_file_folder, monkeypatch):
    hgt_parser_storage = []

    def mockreturn(path):
        # store in outer scope a reference to the mocked parser
        hgt_parser_storage.append(MockHgtParser(path))
        return hgt_parser_storage[0]
    monkeypatch.setattr(gmalthgtparser, 'HgtParser', mockreturn)
    monkeypatch.setattr(os.path, 'isfile', lambda path: True)  # found

    file_handler = Handler(str(filled_file_folder))
    alt = file_handler.get_altitude(10.0, 48.1)

    hgt_parser = hgt_parser_storage[0]
    assert hgt_parser.file == filled_file_folder.join('N10E048.hgt')
    assert hgt_parser.pos == (10.0, 48.1)
    assert hgt_parser.enter_called is True
    assert hgt_parser.exit_called is True
    assert alt == 57


def test_get_altitude_hgt_file_not_found(filled_file_folder, monkeypatch):
    def mockreturn():
        mockreturn.has_been_called = True
        pass
    mockreturn.has_been_called = False

    monkeypatch.setattr(gmalthgtparser, 'HgtParser', mockreturn)
    monkeypatch.setattr(os.path, 'isfile', lambda path: False)  # not found

    file_handler = Handler(str(filled_file_folder))
    alt = file_handler.get_altitude(10.0, 48.1)

    assert mockreturn.has_been_called is False
    assert alt is None
