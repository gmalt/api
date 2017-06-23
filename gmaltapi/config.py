# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Tools to manage the server configuration """

import importlib
import os
import pkgutil

import configobj
import sys
import validate

import gmaltapi.handlers


class GmaltConfigObj(configobj.ConfigObj):
    """ Load the configuration file, read it and return a dict based read
    interface to this configuration

    .. note:: the reading of the configuration file is done in two passes.
        First, it reads the server section to identify the handler
        Then, based on the handler, it loads and reads the handler section,
        instantiate the handler and returns the handler instance as part of
        the configuration

    :param handler_loader: an object to load the correct handler based on
        the type
    :type handler_loader: :class:`gmaltapi.config.HandlerLoader`
    :param str conf_file: path to the INI configuration file
    :param dict spec: a dictionnary to specify the format of the INI file
        sections
    """
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
        """ Load and verify the :class:`configobj.ConfigObj` this
        class is extending using `conf_file` and `spec`

        :param str conf_file: path to the INI configuration file
        :param dict spec: a dictionnary to specify the format of the INI file
            sections
        """
        config_kw = {'configspec': configobj.ConfigObj(spec),
                     'list_values': False,
                     'interpolation': 'Template'}
        super(GmaltConfigObj, self).__init__(conf_file, **config_kw)
        self._verify()

    @staticmethod
    def _build_handler_spec(handler_loader):
        """ Build a configobj compatible attribute spec string to
        validate the handler type set in the server section.

        :param handler_loader: an object to load the correct handler based on
        the type
        :type handler_loader: :class:`gmaltapi.config.HandlerLoader`
        :return: the attribute spec for the handler type attribute in the
            server section
        :rtype: str
        """
        types = []
        for handler in handler_loader.HANDLERS:
            types.append(handler)
        return 'option({}, default=file)'.format(', '.join(types))

    def _verify(self):
        """ Verify the loaded configration using configobj
            :class:`validate.Validator`

        :raise ValueError: if the configuration is not valid
        :return: True if configuration is valid
        :rtype: bool
        """
        validator = validate.Validator()
        validation_result = self.validate(validator, preserve_errors=True)
        result = configobj.flatten_errors(self, validation_result)
        if len(result) != 0:
            raise ValueError(self._format_validate_result(result))
        return True

    @staticmethod
    def _format_validate_result(result):
        """ Helper to format the result of configobj
            :class:`validate.Validator` in a nice human reading form

        :param result: result of :func:`configobj.flatten_errors`
        :type result: list of tuples ([list of sections...], key, result)
        """
        error_text = ""
        for error in result:
            if error[2] is False:
                error_format = "'{1}' in {0} : missing required\n"
            else:
                error_format = "'{1}' in {0} : {2}\n"
            error_text += error_format.format(*error)
        return error_text


class HandlerLoader(object):
    HANDLERS = {}

    def __init__(self):
        self._load_available_handlers()

    def _load_available_handlers(self):
        pkg_path = os.path.dirname(gmaltapi.handlers.__file__)
        available_modules = list(pkgutil.iter_modules([pkg_path]))
        for module_ in available_modules:
            self.HANDLERS[module_[1]] = module_[0]

    def load(self, type_):
        if type_ not in self.HANDLERS:
            raise ValueError('No handler of type {}'.format(type_))

        module_name = 'gmaltapi.handlers.' + type_
        if module_name not in sys.modules:
            importlib.import_module(module_name)

        return getattr(sys.modules[module_name], 'Handler')


def make_config(conf_file, spec):
    handler_loader = HandlerLoader()
    return GmaltConfigObj(handler_loader, conf_file, spec)
