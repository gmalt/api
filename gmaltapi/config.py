import configobj
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
        for handler in handler_loader.HANDLERS:
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


def make_config(conf_file, spec):
    handler_loader = server.HandlerLoader()
    return GmaltConfigObj(handler_loader, conf_file, spec)
