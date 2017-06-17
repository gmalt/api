# -*- coding: utf-8 -*-
#
# (c) 2016 Jonathan Bouzekri
#
# This file is part of the gMalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/fs-service/master/LICENSE

""" Entry point of the fileservice application """

from gevent import monkey
monkey.patch_all()  # noqa

import pkg_resources

from . import server
from . import config


class App(object):
    """ Application main object. In charge of loading the DI container and
    starting the server or workers

    :param str conf_file: path to the config file
    """

    spec = {
        'root': 'string(default="%s")' % pkg_resources.get_distribution('gmaltapi').location,  # noqa
        'server': server.GmaltServer.spec,
        'handler': {}
    }

    def __init__(self, conf_file):
        self.conf = config.make_config(conf_file, self.spec)

    def start_worker(self):
        """ Start the celery worker using the sys.argv configuration """
        # TODO : rework celery instanciation
        return self.get('celery').worker_main()

    def start_server(self):
        try:
            server.GmaltServer(**self.conf['server']).serve_forever()
        except KeyboardInterrupt:
            pass  # silent exit on CTRL+C


def run_server(*args, **kwargs):
    """ Called by console_scripts `gmalt-file-server` to launch the
    API web server

    Usage : `gmalt-file-server conf/gmal.cfg`
    """
    app = App('conf/gmalt.cfg.dev')
    app.start_server()


def run_worker(*args, **kwargs):
    """ Called by console_scripts `gmalt-file-worker` to launch the workers

    It is a wrapper around the standard `celery` command. It accepts the same
    arguments with an additionnal option `-gmalt-config`

    Usage : `gmalt-file-server -P gevent -c 10 -gmalt-config conf/gmal.cfg`
    """
    app = App('conf/gmalt.cfg.dev')
    app.start_worker()
