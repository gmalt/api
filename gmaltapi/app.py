# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Provide the main App class to start the service """

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
