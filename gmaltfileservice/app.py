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

import weedi.loadables_repository as loadables_repository


class ServicesRepository(loadables_repository.LoadablesRepository):
    """ Use setuptools entry point to manage service dependency injection

    .. seealso:: https://github.com/weenect/weedi
    """
    entry_point = 'services'
    conf_section = 'gmalt'


class App(object):
    """ Application main object. In charge of loading the DI container and
    starting the server or workers

    :param str conf_file: path to the config file
    """
    def __init__(self, conf_file):
        self.services = ServicesRepository()
        self.services.load(conf_file)

    def get(self, service_name):
        """ Get a service by its code/name

        :param str service_name: code/name of the service
        :return: the instance of the service
        """
        return self.services[service_name]

    def start_worker(self):
        """ Start the celery worker using the sys.argv configuration """
        return self.get('celery').worker_main()

    def start_server(self):
        """ Start the gevent wsgi webserver """
        return self.get('server').serve_forever()


def run_server(*args, **kwargs):
    """ Called by console_scripts `gmalt-file-server` to launch the
    API web server

    Usage : `gmalt-file-server conf/gmal.cfg`
    """
    app = App('conf/gmalt.cfg')
    app.start_server()


def run_worker(*args, **kwargs):
    """ Called by console_scripts `gmalt-file-worker` to launch the workers

    It is a wrapper around the standard `celery` command. It accepts the same
    arguments with an additionnal option `-gmalt-config`

    Usage : `gmalt-file-server -P gevent -c 10 -gmalt-config conf/gmal.cfg`
    """
    app = App('conf/gmalt.cfg')
    app.start_worker()
