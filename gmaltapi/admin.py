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

import argparse
import os

from .app import App


def run_server(*args, **kwargs):
    """ Called by console_scripts `gmalt-server` to launch the
    gevent API web server

    Usage : `gmalt-server conf/gmalt.cfg`
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file')
    parser.set_defaults(go=lambda config: App(config).start_server())
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        parser.error('Configuration file "%s" doesn\'t exist' % args.config)

    status_code = args.go(args.config)

    return status_code or 0


def run_worker(*args, **kwargs):
    """ Called by console_scripts `gmalt-api-worker` to launch the workers

    It is a wrapper around the standard `celery` command. It accepts the same
    arguments with an additionnal option `-gmalt-config`

    Usage : `gmalt-file-server -P gevent -c 10 -gmalt-config conf/gmal.cfg`
    """
    app = App('conf/gmalt.cfg.dev')
    app.start_worker()
