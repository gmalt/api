import multiprocessing
import socket
import time
import wsgiref.simple_server

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pytest

import gmaltapi.server as server
import gmaltapi.config as config


def pytest_addoption(parser):
    parser.addoption("--folder", type=str, help="specify the folder where "
                                                "the HGT file are stored")


@pytest.fixture
def folder(request):
    return request.config.getoption("--folder")


class ApiWebServer(object):
    def __init__(self, config_data):
        self.config = config_data
        self.host = None
        self.port = None
        self._process = None

    def __enter__(self):
        def worker(q, config_data):
            spec = {'server': server.GmaltServer.spec, 'handler': {}}

            loaded_conf = config.make_config(config_data, spec)
            host = loaded_conf.get('server').get('host')
            port = loaded_conf.get('server').get('port')
            app = loaded_conf.get('server').get('handler')

            q.put((host, port))

            wsgiref \
                .simple_server \
                .make_server(host, port, server.WSGIHandler(app)) \
                .serve_forever()

        queue = multiprocessing.Queue()

        self._process = multiprocessing.Process(
            target=worker, args=(queue, self.config,)
        )

        self._process.start()

        self.host, self.port = queue.get()

        # We must wait for the server to start listening, but give up
        # after a specified maximum timeout
        timeout = 5
        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time)
            if elapsed_time > timeout:
                self.terminate()
                raise RuntimeError(
                    "Failed to start the server after %d seconds. " % timeout
                )

            if self._can_ping_server():
                break

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def get_base_url(self):
        return 'http://{}:{}'.format(self.host, self.port)

    def get_url(self):
        return '{}/altitude'.format(self.get_base_url())

    def terminate(self):
        if self._process:
            self._process.terminate()

    def _can_ping_server(self):
        if not self.port:
            return False

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
        except socket.error:
            success = False
        else:
            success = True
        finally:
            sock.close()

        return success


class ResetStingIO(StringIO):
    def read(self, *args, **kwargs):
        read_value = StringIO.read(self, *args, **kwargs)
        self.seek(0)
        return read_value
