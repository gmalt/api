# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Classes to handle gmalt API request with WSGI """

import importlib
import os
import sys
import pkgutil
import json
import logging

from marshmallow import Schema, fields, pre_load
from webob import Request, Response
import webob.exc
from routr import route, GET, POST, OPTIONS
from routr.exc import NoMatchFound

import gmaltapi.handlers


class AltSchema(Schema):
    """ A helper class to validate the query parameters of
    the elevation endpoint.
    """
    lat = fields.Number(required=True, allow_none=False)
    lng = fields.Number(required=True, allow_none=False)

    @pre_load()
    def read_params(self, req):
        """ Control how :mod:`marshmallow` reads data from the
        :class:`webob.Request` object

        :param req: the request object
        :type req: :class:`webob.Request`
        :return: dict with `lat` and `lng`
        :rtype: dict
        """
        params = {}
        if 'lat' in req.params:
            params['lat'] = req.params.get('lat', None)
        if 'lng' in req.params:
            params['lng'] = req.params.get('lng', None)
        return params


class WSGIHandler(object):
    """ gmalt API core WSGI handler that :
        - reads the request
        - route it (to `/altitude`)
        - get elevation from handler based on request params
        - manage exception and error messages
        - create and return response

    :param handler: elevation handler
    :type handler: :class:`gmaltapi.handlers.files.Handler` or any class
        implementing the `get_altitude` method
    """
    def __init__(self, alt_handler):
        self.alt_handler = alt_handler
        self.schema = AltSchema()
        self.router = route("",
                            route(GET,  "/altitude", self.get_altitude),
                            route(POST, "/altitude", self.get_altitude),
                            route(OPTIONS, "/altitude", self.options_altitude))

    def __call__(self, environ, start_response):
        """ WSGI callable

        :param dict environ: WSGI environment dict
        :param func start_response: the WSGI response function
        :return: a response object compatible with WSGI middlewares
        :rtype: :class:`webob.Response`
        """
        try:
            req = Request(environ)
            body = self.router(req).target(req)
            status_code = 200
        except webob.exc.HTTPBadRequest as e:
            status_code = 400
            body = e.detail
        except NoMatchFound as e:
            status_code = 404
            explanation = e.response.explanation
            body = {'message': explanation + ' Use GET /altitude instead.',
                    'code': status_code, 'title': e.response.title}
        except webob.exc.WSGIHTTPException as e:
            status_code = e.status_code
            body = {'message': str(e), 'code': status_code,
                    'title': e.title}
        except Exception as e:
            logging.exception(e)
            status_code = 500
            explanation = 'An error occured. check the log file on the server.'
            body = {'message': explanation, 'code': status_code,
                    'title': 'Internal Server Error'}

        res = Response()
        res.status_code = status_code
        body_text = json.dumps(body) if body else u''
        res.body = body_text.encode('utf-8')
        res.content_type = 'application/json' if body else 'text/plain'

        return res(environ, start_response)

    def get_altitude(self, req):
        """ GET /altitude
        Returns the requested elevation value from HTTP params in request

        :param req: HTTP request object
        :type req: :class:`webob.Request`
        :return: dict with elevation value found
        :rtype: dict with the key `alt`
        :raises: :class:`webob.exc.HTTPBadRequest` if any error in the request
        """
        result = self.schema.load(req)
        if result.errors:
            raise webob.exc.HTTPBadRequest(detail=result.errors)
        return {'alt': self.alt_handler.get_altitude(**result.data)}

    def options_altitude(self, req):
        """ OPTIONS /altitude
        Authorize OPTIONS query for easy CORS

        :param req: HTTP request object
        :type req: :class:`webob.Request`
        :return: empty string
        :rtype: unicode
        """
        return u''


class HandlerLoader(object):
    """ Load handlers from :mod:`gmaltapi.handlers` package

    .. note:: use the global instance from this module
        `handler_loader`
    """
    HANDLERS = {}

    def __init__(self):
        self._load_available_handlers()

    def _load_available_handlers(self):
        """ Load handlers from the package :mod:`gmaltapi.handlers`
        updates the `HANDLERS` class dict attribute with the
        type of the handler as key and the module as value
        """
        pkg_path = os.path.dirname(gmaltapi.handlers.__file__)
        available_modules = list(pkgutil.iter_modules([pkg_path]))
        for module_ in available_modules:
            self.HANDLERS[module_[1]] = module_[0]

    def load(self, type_):
        """ Get a handler class of a specific type

        :param str type_: type of the handler to load
        :return: a handler class
        :raise ValueError: if the handler type is unknown
        """
        if type_ not in self.HANDLERS:
            raise ValueError('No handler of type {}'.format(type_))

        module_name = 'gmaltapi.handlers.' + type_
        if module_name not in sys.modules:
            importlib.import_module(module_name)

        return getattr(sys.modules[module_name], 'Handler')


#: instance of the handler loader to be used in other modules
handler_loader = HandlerLoader()


def build_gmalt_handler(handler_type, handler_conf):
    """ Helper function to create a gmalt handler

    :param str handler_type: the type of the handler to create
    :param dict handler_conf: the handler configuration on instanciation
    :return: gmalt handler
    :rtype: :class:`gmaltapi.handler.WSGIHandler`
    """
    handler_class = handler_loader.load(handler_type)
    return handler_class(**handler_conf)


def build_wsgi_handler(handler_type, handler_conf):
    """ Helper function to create a WSGI handler

    :param str handler_type: the type of the handler to create
    :param dict handler_conf: the handler configuration on instanciation
    :return: a WSGI handler wrapping the gmalt handler
    """
    return WSGIHandler(build_gmalt_handler(handler_type, handler_conf))
