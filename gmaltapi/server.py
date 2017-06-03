# -*- coding: utf-8 -*-
#
# (c) 2016 Jonathan Bouzekri
#
# This file is part of the gMalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/fs-service/master/LICENSE

""" Webservice HTTP REST API """

import importlib
import json
import os
import pkgutil

import sys

import logging
from gevent.pywsgi import WSGIServer
from marshmallow import Schema, fields, pre_load
from webob import Request, Response
import webob.exc
from routr import route, GET, POST, OPTIONS
from routr.exc import NoMatchFound

import gmaltapi.handlers


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


class AltSchema(Schema):
    lat = fields.Number(required=True, allow_none=False)
    lng = fields.Number(required=True, allow_none=False)

    @pre_load()
    def read_params(self, req):
        params = {}
        if 'lat' in req.params:
            params['lat'] = req.params.get('lat', None)
        if 'lng' in req.params:
            params['lng'] = req.params.get('lng', None)
        return params


class WSGIHandler(object):
    """ Manage exception to return formatted message to client

    :param handler: WSGI callable
    """
    def __init__(self, alt_handler):
        self.alt_handler = alt_handler
        self.schema = AltSchema()
        self.router = route("",
                            route(GET,  "/altitude", self.get_altitude),
                            route(POST, "/altitude", self.get_altitude),
                            route(OPTIONS, "/altitude", self.options_altitude))

    def __call__(self, environ, start_response):
        try:
            req = Request(environ)
            body = self.router(req).target(req)
            status_code = 200
        except webob.exc.HTTPBadRequest as e:
            status_code = 400
            body = e.detail
        except NoMatchFound as e:
            status_code = 404
            body = {'message': e.response.explanation + ' Use GET /altitude instead.',
                    'code': status_code, 'title': e.response.title}
        except webob.exc.WSGIHTTPException as e:
            status_code = e.status_code
            body = {'message': e.explanation, 'code': status_code, 'title': e.title}
        except Exception as e:
            logging.exception(e)
            status_code = 500
            body = {'message': 'An error occured. check the log file on the server.',
                    'code': status_code, 'title': 'Internal Server Error'}

        res = Response()
        res.status_code = status_code
        res.body = json.dumps(body)
        res.content_type = 'application/json'

        return res(environ, start_response)

    def get_altitude(self, req):
        result = self.schema.load(req)
        if result.errors:
            raise webob.exc.HTTPBadRequest(detail=result.errors)
        return {'alt': self.alt_handler.get_altitude(**result.data)}

    def options_altitude(self, req):
        pass


class GmaltServer(WSGIServer):
    """ A gevent webserver API to request elevation data

    :param str host: host or ip binded to
    :param int port: port binded to
    :param celery_service: the celery instance
    :type celery_service: :class:`gmaltfileservice.task.GmaltCelery`
    """

    spec = {
        'handler': 'string(default="file")',
        'host': 'string(default="localhost")',
        'port': 'integer(default=8088)'
    }

    def __init__(self, handler, host, port):
        super(GmaltServer, self).__init__((host, port), WSGIHandler(handler))

    def serve_forever(self, stop_timeout=None):
        print('Serving on %s:%d' % self.address)
        super(GmaltServer, self).serve_forever(stop_timeout=stop_timeout)
