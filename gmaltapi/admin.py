# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Entry point of the gmaltapi application """

from gevent import monkey
monkey.patch_all()  # noqa

from .app import App


def run_server(*args, **kwargs):
    """ Called by console_scripts `gmalt-api-server` to launch the
    API web server

    Usage : `gmalt-api-server conf/gmalt.cfg`
    """
    app = App('conf/gmalt.cfg.dev')
    app.start_server()


def run_worker(*args, **kwargs):
    """ Called by console_scripts `gmalt-api-worker` to launch the workers

    It is a wrapper around the standard `celery` command. It accepts the same
    arguments with an additionnal option `-gmalt-config`

    Usage : `gmalt-file-server -P gevent -c 10 -gmalt-config conf/gmal.cfg`
    """
    app = App('conf/gmalt.cfg.dev')
    app.start_worker()
