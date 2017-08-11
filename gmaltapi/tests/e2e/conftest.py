# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Module providing configuration for pytest to run e2e tests """

import multiprocessing
import socket
import time
import wsgiref.simple_server

import pytest

from .. import ResetStingIO  # noqa

import gmaltapi.config as config
import gmaltapi.app as app


def pytest_addoption(parser):
    """ Add a `--folder` option to pytest CLI """
    parser.addoption("--folder", type=str, help="specify the folder where "
                                                "the HGT file are stored")


@pytest.fixture
def folder(request):
    """ A pytest fixture to inject the value of the `--folder` option
    provided in the pytest CLI thanks to
    :func:`gmaltapi.tests.e2e.conftest.pytest_addoption`

    :return: the `--folder` value from the CLI
    :rtype: str
    """
    return request.config.getoption("--folder")


class ApiWebServer(object):
    """ A context manager that runs a gmalt api server in a dedicated
    process based on provided configuration

    Usage::

        my_running_server = ApiWebServer('path/to/config/file.cfg')
        with my_running_server:
            assert get_altitude(0.99, 10.01) == 57

    .. note:: this is heavily inspired from the `Flask-Testing
        <https://github.com/jarus/flask-testing>`_. extension and its
        LiveServerTestCase class

    :param config_data: the configuration data as a path to a file or
        a FileObject compatible interface
    :type: str or `file object`
    """
    def __init__(self, config_data):
        self.config = config_data
        self.host = None
        self.port = None
        self._process = None

    def __enter__(self):
        loaded_conf = config.GmaltServerConfigObj(self.config, app.App.spec)
        self.host = loaded_conf.get('server').get('host')
        self.port = loaded_conf.get('server').get('port')
        handler = loaded_conf.get('server').get('handler')

        def worker(host, port, handler):
            wsgiref \
                .simple_server \
                .make_server(host, port, handler) \
                .serve_forever()

        self._process = multiprocessing.Process(
            target=worker, args=(self.host, self.port, handler)
        )

        self._process.start()

        # We must wait for the server to start listening, but give up
        # after a specified maximum timeout
        timeout = 5
        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time)
            if elapsed_time > timeout:
                self.terminate()
                raise RuntimeError(
                    "Failed to start the server after %d seconds. " % timeout
                )

            if self._can_ping_server():
                break

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def get_base_url(self):
        """ Get the live test server base url without trailing /

        :return: the base url of the test server
        :rtype: str
        """
        return 'http://{}:{}'.format(self.host, self.port)

    def get_url(self):
        """ Get the full url of the gmalt altitude API

        :return: the API url
        :rtype: str
        """
        return '{}/altitude'.format(self.get_base_url())

    def terminate(self):
        if self._process:
            self._process.terminate()

    def _can_ping_server(self):
        if not self.port:
            return False

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
        except socket.error:
            success = False
        else:
            success = True
        finally:
            sock.close()

        return success
