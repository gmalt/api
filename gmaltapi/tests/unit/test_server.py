# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Unit test of :mod:`gmaltapi.server` """

import pytest
import webob
import webob.exc

import gmaltapi.server as server


class TestAltShema(object):
    def test_read_params_empty(self):
        alt_schema = server.AltSchema()
        params = alt_schema.read_params(webob.Request({}))
        assert 'lat' not in params
        assert 'lng' not in params

    def test_read_params(self):
        req = webob.Request({'QUERY_STRING': 'lat=1.001&lng=10.001'})
        alt_schema = server.AltSchema()
        params = alt_schema.read_params(req)
        assert params['lat'] == '1.001'
        assert params['lng'] == '10.001'


class TestWSGIHandler(object):
    @pytest.mark.parametrize("method", ['GET', 'POST'])
    def test__call__altitude(self, mock_handler, mock_response, method):
        env = {'REQUEST_METHOD': method, 'PATH_INFO': '/altitude',
               'QUERY_STRING': 'lat=1.001&lng=10.001'}
        wsgi_app = server.WSGIHandler(mock_handler)

        result = wsgi_app(env, mock_response)

        assert result == ['{"alt": 57}'.encode('utf-8')]
        assert mock_handler.lat == 1.001
        assert mock_handler.lng == 10.001
        assert mock_response.status == '200 OK'

        res_headers = [('Content-Length', '11'),
                       ('Content-Type', 'application/json')]
        assert mock_response.response_headers == res_headers

    def test__call__options_altitude(self, mock_handler, mock_response):
        env = {'REQUEST_METHOD': 'OPTIONS', 'PATH_INFO': '/altitude',
               'QUERY_STRING': 'lat=1.001&lng=10.001'}
        wsgi_app = server.WSGIHandler(mock_handler)

        result = wsgi_app(env, mock_response)

        assert result == [''.encode('utf-8')]
        assert mock_handler.lat is None
        assert mock_handler.lng is None
        assert mock_response.status == '200 OK'

        res_headers = [('Content-Length', '0'),
                       ('Content-Type', 'text/plain; charset=UTF-8')]
        assert mock_response.response_headers == res_headers

    @pytest.mark.parametrize("method", ['GET', 'POST'])
    def test__call__altitude_no_params(self, mock_handler, mock_response,
                                       method):
        env = {'REQUEST_METHOD': method, 'PATH_INFO': '/altitude',
               'QUERY_STRING': ''}
        wsgi_app = server.WSGIHandler(mock_handler)

        result = wsgi_app(env, mock_response)

        msg1 = '{"lat": ["Missing data for required field."], ' \
               '"lng": ["Missing data for required field."]}'.encode('utf-8')
        msg2 = '{"lng": ["Missing data for required field."], ' \
               '"lat": ["Missing data for required field."]}'.encode('utf-8')
        assert result in [[msg1], [msg2]]

        assert mock_handler.lat is None
        assert mock_handler.lng is None
        assert mock_response.status == '400 Bad Request'

        res_headers = [('Content-Length', '90'),
                       ('Content-Type', 'application/json')]
        assert mock_response.response_headers == res_headers

    @pytest.mark.parametrize("method", ['GET', 'POST'])
    def test__call__altitude_empty_params(self, mock_handler, mock_response,
                                          method):
        env = {'REQUEST_METHOD': method, 'PATH_INFO': '/altitude',
               'QUERY_STRING': 'lat=&lng='}
        wsgi_app = server.WSGIHandler(mock_handler)

        result = wsgi_app(env, mock_response)

        msg1 = '{"lat": ["Not a valid number."], ' \
               '"lng": ["Not a valid number."]}'.encode('utf-8')
        msg2 = '{"lng": ["Not a valid number."], ' \
               '"lat": ["Not a valid number."]}'.encode('utf-8')
        assert result in [[msg1], [msg2]]

        assert mock_handler.lat is None
        assert mock_handler.lng is None
        assert mock_response.status == '400 Bad Request'

        res_headers = [('Content-Length', '64'),
                       ('Content-Type', 'application/json')]
        assert mock_response.response_headers == res_headers

    @pytest.mark.parametrize("method", ['GET', 'POST'])
    def test__call__altitude_wrong_params(self, mock_handler, mock_response,
                                          method):
        env = {'REQUEST_METHOD': method, 'PATH_INFO': '/altitude',
               'QUERY_STRING': 'lat=notanumber&lng=notanumber'}
        wsgi_app = server.WSGIHandler(mock_handler)

        result = wsgi_app(env, mock_response)

        msg1 = '{"lat": ["Not a valid number."], ' \
               '"lng": ["Not a valid number."]}'.encode('utf-8')
        msg2 = '{"lng": ["Not a valid number."], ' \
               '"lat": ["Not a valid number."]}'.encode('utf-8')
        assert result in [[msg1], [msg2]]

        assert mock_handler.lat is None
        assert mock_handler.lng is None
        assert mock_response.status == '400 Bad Request'

        res_headers = [('Content-Length', '64'),
                       ('Content-Type', 'application/json')]
        assert mock_response.response_headers == res_headers

    @pytest.mark.parametrize("method", ['GET', 'POST', 'OPTIONS'])
    def test__call__route_not_found(self, mock_handler, mock_response,
                                    method):
        env = {'REQUEST_METHOD': method, 'PATH_INFO': '/unknownroute',
               'QUERY_STRING': 'lat=1.001&lng=10.001'}
        wsgi_app = server.WSGIHandler(mock_handler)

        result = wsgi_app(env, mock_response)

        msg1 = '{"message": "The resource could not be found. Use GET ' \
               '/altitude instead.", "code": 404, "title": ' \
               '"Not Found"}'.encode('utf-8')
        msg2 = '{"message": "The resource could not be found. Use GET ' \
               '/altitude instead.", "title": "Not Found", ' \
               '"code": 404}'.encode('utf-8')
        msg3 = '{"code": 404, "message": "The resource could not be found. ' \
               'Use GET /altitude instead.", ' \
               '"title": "Not Found"}'.encode('utf-8')
        msg4 = '{"code": 404, "title": "Not Found", "message": "The resource' \
               ' could not be found. Use GET /altitude instead.' \
               '"}'.encode('utf-8')
        msg5 = '{"title": "Not Found", "message": "The resource could not be' \
               ' found. Use GET /altitude instead.", "code": ' \
               '404}'.encode('utf-8')
        msg6 = '{"title": "Not Found", "code": 404, "message": "The resource' \
               ' could not be found. Use GET /altitude instead.' \
               '"}'.encode('utf-8')
        assert result in [[msg1], [msg2], [msg3], [msg4], [msg5], [msg6]]

        assert mock_handler.lat is None
        assert mock_handler.lng is None
        assert mock_response.status == '404 Not Found'

        res_headers = [('Content-Length', '109'),
                       ('Content-Type', 'application/json')]
        assert mock_response.response_headers == res_headers

    @pytest.mark.parametrize("method", ['GET', 'POST', 'OPTIONS'])
    def test__call__wsgi_exception(self, mock_handler, mock_response,
                                   method, monkeypatch):
        def mockreturn(*args, **kwargs):
            raise webob.exc.WSGIHTTPException(detail="error message")
        monkeypatch.setattr(webob.Request, '__init__', mockreturn)

        env = {'REQUEST_METHOD': method, 'PATH_INFO': '/altitude',
               'QUERY_STRING': 'lat=1.001&lng=10.001'}
        wsgi_app = server.WSGIHandler(mock_handler)

        result = wsgi_app(env, mock_response)

        msg1 = '{"message": "error message", "code": 500, "title": "Internal' \
               ' Server Error"}'.encode('utf-8')
        msg2 = '{"message": "error message", "title": "Internal Server Error' \
               '", "code": 500}'.encode('utf-8')
        msg3 = '{"code": 500, "title": "Internal Server Error", "message": "' \
               'error message"}'.encode('utf-8')
        msg4 = '{"code": 500, "message": "error message", "title": "Internal' \
               ' Server Error"}'.encode('utf-8')
        msg5 = '{"title": "Internal Server Error", "message": "error message' \
               '", "code": 500}'.encode('utf-8')
        msg6 = '{"title": "Internal Server Error", "code": 500, "message": ' \
               '"error message"}'.encode('utf-8')
        assert result in [[msg1], [msg2], [msg3], [msg4], [msg5], [msg6]]

        assert mock_handler.lat is None
        assert mock_handler.lng is None
        assert mock_response.status == '500 Internal Server Error'

        res_headers = [('Content-Length', '75'),
                       ('Content-Type', 'application/json')]
        assert mock_response.response_headers == res_headers

    @pytest.mark.parametrize("method", ['GET', 'POST', 'OPTIONS'])
    def test__call__exception(self, mock_handler, mock_response,
                              method, monkeypatch):
        def mockreturn(*args, **kwargs):
            raise Exception("error message")
        monkeypatch.setattr(webob.Request, '__init__', mockreturn)

        env = {'REQUEST_METHOD': method, 'PATH_INFO': '/altitude',
               'QUERY_STRING': 'lat=1.001&lng=10.001'}
        wsgi_app = server.WSGIHandler(mock_handler)

        result = wsgi_app(env, mock_response)

        msg1 = '{"message": "An error occured. check the log file on the ' \
               'server.", "code": 500, "title": "Internal Server ' \
               'Error"}'.encode('utf-8')
        msg2 = '{"message": "An error occured. check the log file on the ' \
               'server.", "title": "Internal Server Error", ' \
               '"code": 500}'.encode('utf-8')
        msg3 = '{"code": 500, "message": "An error occured. check the log ' \
               'file on the server.", "title": "Internal Server ' \
               'Error"}'.encode('utf-8')
        msg4 = '{"code": 500, "title": "Internal Server Error", "message": ' \
               '"An error occured. check the log file on the ' \
               'server."}'.encode('utf-8')
        msg5 = '{"title": "Internal Server Error", "code": 500, "message": ' \
               '"An error occured. check the log file on the ' \
               'server."}'.encode('utf-8')
        msg6 = '{"title": "Internal Server Error", "message": "An error ' \
               'occured. check the log file on the server.", ' \
               '"code": 500}'.encode('utf-8')
        assert result in [[msg1], [msg2], [msg3], [msg4], [msg5], [msg6]]
        assert mock_handler.lat is None
        assert mock_handler.lng is None
        assert mock_response.status == '500 Internal Server Error'

        res_headers = [('Content-Length', '113'),
                       ('Content-Type', 'application/json')]
        assert mock_response.response_headers == res_headers
