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

import configobj
import pkg_resources
import validate

from . import server


class GmaltConfigObj(configobj.ConfigObj):
    def __init__(self, handler_loader, conf_file, spec):
        # First load current config to extract the configured handler
        spec['server']['handler'] = self._build_handler_spec(handler_loader)
        self._fill_parent(conf_file, spec)

        # Then based on the handler update spec and reload config
        handler_class = handler_loader.load(self['server']['handler'])
        spec['handler'] = handler_class.spec
        self.reset()
        self._fill_parent(conf_file, spec)

        # Fill the configuration with the handler instance
        self['server']['handler'] = handler_class(**self['handler'])

    def _fill_parent(self, conf_file, spec):
        config_kw = {'configspec': configobj.ConfigObj(spec),
                     'list_values': False,
                     'interpolation': 'Template'}
        super(GmaltConfigObj, self).__init__(conf_file, **config_kw)
        self._verify()

    @staticmethod
    def _build_handler_spec(handler_loader):
        types = []
        for handler in handler_loader.HANDLERS.keys():
            types.append(handler)
        return 'option({}, default=file)'.format(', '.join(types))

    def _verify(self):
        validator = validate.Validator()
        validation_result = self.validate(validator, preserve_errors=True)
        result = configobj.flatten_errors(self, validation_result)
        if len(result) != 0:
            raise ValueError(self._format_validate_result(result))
        return True

    @staticmethod
    def _format_validate_result(result):
        error_text = ""
        for error in result:
            if error[2] is False:
                error_format = "'{1}' in {0} : missing required\n"
            else:
                error_format = "'{1}' in {0} : {2}\n"
            error_text += error_format.format(*error)
        return error_text


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
        self.handler_loader = server.HandlerLoader()
        self.conf = GmaltConfigObj(self.handler_loader, conf_file, self.spec)

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
