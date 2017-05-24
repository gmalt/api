# -*- coding: utf-8 -*-
#
# (c) 2016 Jonathan Bouzekri
#
# This file is part of the gMalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/fs-service/master/LICENSE

""" Webservice HTTP REST API """

from sys import exc_info
from traceback import format_tb
from gevent.pywsgi import WSGIServer
import weedi.loadable as loadable


class WSGIExceptionMiddleware(object):
    """ Manage exception to return formatted message to client

    :param task: the celery instance
    :type task: :class:`gmaltfileservice.task.GmaltCelery`
    :param handler: WSGI callable
    """
    def __init__(self, server, handler):
        self.server = server
        self.application = handler

    def __call__(self, environ, start_response):
        """ Exception formatting WSGI handler """
        try:
            return self.application(self.server, environ, start_response)
        except:
            e_type, e_value, tb = exc_info()
            traceback = ['Traceback (most recent call last):']
            traceback += format_tb(tb)
            traceback.append('%s: %s' % (e_type.__name__, e_value))
            try:
                start_response('500 INTERNAL SERVER ERROR', [
                               ('Content-Type', 'text/plain')])
            except:
                pass
            print('\n'.join(traceback))
        return ['\n'.join(traceback).encode('utf-8')]


def get_altitude_handler(task, environ, start_response):
    """ Handler to schedule a task to get an elevation value

    :param task: the celery instance
    :type task: :class:`gmaltfileservice.task.GmaltCelery`
    :param environ: WSGI environment
    :param start_response: WSGI start_response
    :return: list of WSGI binary body response
    """
    print(task.altitude.delay(4, 4).get())
    if environ['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b"<b>hello world</b>"]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>Not Found</h1>']


class GmaltServer(WSGIServer, loadable.Service):
    """ A gevent webserver API to request elevation data

    :param str host: host or ip binded to
    :param int port: port binded to
    :param celery_service: the celery instance
    :type celery_service: :class:`gmaltfileservice.task.GmaltCelery`
    """
    spec = {
        'host': 'string(default="localhost")',
        'port': 'integer(default=8088)',
    }

    def __init__(self, host, port, celery_service):
        super(GmaltServer, self).__init__(
            (host, port),
            WSGIExceptionMiddleware(celery_service, get_altitude_handler))

    def serve_forever(self):
        print('Serving on %s:%d' % self.address)
        super(GmaltServer, self).serve_forever()
