gmalt API - Usage
=================

gmalt API is a standard HTTP JSON REST API.

It provides a single endpoint `GET /altitude` that takes 2 mandatory parameters (to be passed as a query string) :

- ``lat`` : the latitude of the position as a float
- ``lng`` : the longitude of the position as a float

An it returns a JSON like this that represents the altitude in meters of the requested position :

.. code-block:: json

    {
        "alt": 57
    }

.. note:: if the altitude is not available (either because it is outside the available range of the SRTM dataset or
there is no value at this point), it returns ``null``.

In case of an error, you can meet 2 different responses.

The first one in case of invalid parameters (error 400) :

.. code-block:: json

    {
        "lat": ["message explaining the error"],
        "lng": ["message explaining the error"]
    }

The second one in case of an error (other error codes) :

.. code-block:: json

    {
        "message": "detail of the error",
        "code": the error code as an integer,
        "title": "title related to the error code"
    }

A simple client using the awesome python ``requests`` library :

.. code-block:: python

    import requests

    alt = requests.get('http://localhost:8088/altitude', params={'lat': 0.9999, 'lng': 10.0001})
    assert alt.status_code == 200
    assert alt.json().get('alt') == 57
