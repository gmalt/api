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

import pkg_resources

from . import server
from . import config


class App(object):
    """ Application main object. In charge of loading the configuration,
    initializing and starting the server

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
        """ Start the gevent wsgi server """
        try:
            server.GmaltServer(**self.conf['server']).serve_forever()
        except KeyboardInterrupt:
            pass  # silent exit on CTRL+C


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
