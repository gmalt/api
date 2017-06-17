import pytest
import requests

from .conftest import ApiWebServer, ResetStingIO


@pytest.fixture
def file_server(folder):
    conf = ResetStingIO("""
    [server]
    handler = file

    [handler]
    folder = {}
    """.format(folder))
    return ApiWebServer(conf)


def test_get_altitude(file_server):
    with file_server:
        alt = requests.get(file_server.get_url(), params={'lat': 0.9999, 'lng': 10.0001})
        print(alt.status_code, alt.text)

