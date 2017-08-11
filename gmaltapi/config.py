# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Tools to manage the server configuration """

import configobj
import validate

import gmaltapi.handler as handler


class GmaltConfigObj(configobj.ConfigObj):
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


class GmaltServerConfigObj(GmaltConfigObj):
    """ Load the configuration file, read it and return a dict based read
    interface to this configuration

    .. note:: the reading of the configuration file is done in two passes.
        First, it reads the server section to identify the handler
        Then, based on the handler, it loads and reads the handler section,
        instantiate the handler and returns the handler instance as part of
        the configuration

    :param str conf_file: path to the INI configuration file
    :param dict spec: a dictionnary to specify the format of the INI file
        sections
    :param bool create_handler: if True, replace handler type with handler
        instance in server config
    """
    def __init__(self, conf_file, spec, create_handler=True):
        # First load current config to extract the configured handler
        spec['server']['handler'] = self._build_handler_spec()
        self._fill_parent(conf_file, spec)

        handler_type = self['server']['handler']
        spec['handler'] = handler.handler_loader.load(handler_type).spec
        self.reset()
        self._fill_parent(conf_file, spec)

        # Fill the configuration with the handler instance
        if create_handler:
            handler_obj = handler.build_wsgi_handler(handler_type,
                                                     self['handler'])
            self['server']['handler'] = handler_obj

    @staticmethod
    def _build_handler_spec():
        """ Build a configobj compatible attribute spec string to
        validate the handler type set in the server section.

        :return: the attribute spec for the handler type attribute in the
            server section
        :rtype: str
        """
        types = []
        for handler_type in handler.handler_loader.HANDLERS:
            types.append(handler_type)
        return 'option({}, default=file)'.format(', '.join(types))
