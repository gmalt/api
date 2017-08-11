# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Provide a gevent server to serve gmalt API """

from gevent.pywsgi import WSGIServer


class GmaltServer(WSGIServer):
    """ A gevent webserver API to request elevation data

    :param handler: the handler instance to load elevation data from
        latitude and longitude
    :type handler: :class:`gmaltapi.handlers.files.Handler` or any class
        implementing the `get_altitude` method
    :param str host: host or ip binded to
    :param int port: port binded to
    :param str cors: optional CORS domains to enable CORS headers
    """

    spec = {
        'handler': 'string(default="file")',
        'host': 'string(default="localhost")',
        'port': 'integer(default=8088)',
        'cors': 'string(default=None)',
        'pool_size': 'integer(default=None)'
    }

    def __init__(self, handler, host, port, cors=None, **kwargs):
        pool_size = kwargs.pop('pool_size') or 'default'
        super(GmaltServer, self).__init__((host, port),
                                          self._build_wsgi(handler, cors),
                                          spawn=pool_size, **kwargs)

    def _build_wsgi(self, handler, cors):
        if cors:
            from wsgicors import CORS
            handler = CORS(handler, methods="GET, OPTIONS, POST", origin=cors)
        return handler

    def serve_forever(self, stop_timeout=None):
        """ Start the server """
        print('Serving on %s:%d' % self.address)
        super(GmaltServer, self).serve_forever(stop_timeout=stop_timeout)
