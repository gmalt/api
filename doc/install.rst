gmalt API - Installation
========================


Global from PyPI
----------------

If you want to install this package globally at the OS level, you can install it from PyPI.

Just run this command in a terminal:

.. code-block:: console

    $ sudo pip install gmaltapi

After installation, the commands should be available:

.. code-block:: console

    $ which gmalt-server
    /usr/bin/gmalt-server
    $ which gmalt-worker
    /usr/bin/gmalt-worker


Local in a virtualenv
---------------------

Clone the repository, create and activate a virtualenv then install dependencies :

.. code-block:: console

    $ git clone git@github.com:gmalt/api.git gmalt-api
    $ cd gmalt-api
    $ virtualenv venv
    $ . venv/bin/activate
    $ python setup.py develop

the CLI commands should be available:

.. code-block:: console

    $ which gmalt-server
    .../venv/bin/gmalt-server
    $ which gmalt-worker
    .../venv/bin/gmalt-worker


Configuration
-------------

Once the server command line available, you need to configure the web server. You can look into the file `conf/gmalt.cfg.j2 <https://github.com/gmalt/api/blob/master/conf/gmalt.cfg.j2>`_
to have a full description of the config options.

You can copy this file and edit it :

.. code-block:: console

    $ cp conf/gmalt.cfg.j2 conf/gmalt.cfg

First you have to configure the ``server`` section :

.. code-block:: ini

    [server]
    host = localhost
    port = 8088
    pool_size = 1000
    handler = file

This configuration will start a server listening on ``localhost`` and port ``8088``. It will serve at most 1000 concurrent requests and use the handler ``file`` to get the elevation values.
Only the handler is mandatory, the other parameters are optionals (note that ``pool_size`` is infinite per default).

Then you have to configure the ``handler`` section. The settings in this section will change according to your choice of handler in the ``server`` section.
Please refer to each handler documentation for more information.


Startup
-------

Once configured, you can run the command :

.. code-block:: console

    $ gmalt-server path/to/my/conf/gmalt.cfg
    Serving on localhost:8088

Provided that you have correctly configured the ``handler`` section (see next chapter), the API is ready to accept request.

.. note:: I recommend using either a proxy like nginx in front of the API server (that is powered by ``gevent.pywsgi``) or to use a WSGI HTTP server like gunicorn behind nginx.


Handlers
--------

In the ``server`` section of the configuration file, you have an attribute ``handler``. Per default, its value is ``file``.

This attribute indicates how gmalt API is going to get the elevation value for the requested position. Moreover, based on the chosen value, you will have to configure the ``handler`` section accordingly.
This is detailed in the page dedicated to each handler.

The available values are :
    - `file <https://github.com/gmalt/api/blob/master/doc/storage_file.rst>`_ : raw SRTM HGT file are stored on the filesystem and read on each query
    - `celery <https://github.com/gmalt/api/blob/master/doc/storage_file.rst>`_ : raw HGT file are stored on the filesystem and a celery worker read file on each query (TODO)
    - `postgres <https://github.com/gmalt/api/blob/master/doc/storage_postgres.rst>`_ : elevation data are loaded in a standard PostgresSQL table (TODO)
    - `postgis <https://github.com/gmalt/api/blob/master/doc/storage_postgis.rst>`_ : elevation data are loaded in a PostGIS SQL table with raster support (TODO)
