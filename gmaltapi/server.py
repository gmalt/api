# -*- coding: utf-8 -*-
#
# (c) 2016 Jonathan Bouzekri
#
# This file is part of the gMalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/fs-service/master/LICENSE

""" Webservice HTTP REST API """

import json

from gevent.pywsgi import WSGIServer
from webob import Request, Response


class WSGIHandler(object):
    """ Manage exception to return formatted message to client

    :param handler: WSGI callable
    """
    def __init__(self, handler_type):
        self.handler_type = handler_type

    def __call__(self, environ, start_response):
        res = Response()

        try:
            req = Request(environ)

            altitude = 52

            res.body = json.dumps({'altitude': altitude})
            res.content_type = 'application/json'
        except:
            res.status_code = 500
            req.body = json.dumps({'error': 'An error occured. check the log file on the server.'})
        return res(environ, start_response)


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

    def serve_forever(self):
        print('Serving on %s:%d' % self.address)
        super(GmaltServer, self).serve_forever()
