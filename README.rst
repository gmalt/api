gmalt API
=========

.. image:: https://travis-ci.org/gmalt/api.svg?branch=master
    :target: https://travis-ci.org/gmalt/api

gmalt API provides the web server to get an altitude at a geographical position using the SRTM dataset.

It is designed to handler SRTM data stored in :

- raw HGT file
- standard SQL table (coming soon)
- GIS aware SQL table with raster format (coming soon)

For now, only postgres (with PostGIS for raster support) is supported as SQL storage.


Documentation
-------------

- `Installation <https://github.com/gmalt/api/blob/master/doc/install.rst>`_
- Configuration :
    - `Raw HGT file in the filesystem <https://github.com/gmalt/api/blob/master/doc/storage_file.rst>`_
    - `Raw HGT file in the filesystem with a celery worker <https://github.com/gmalt/api/blob/master/doc/storage_celery.rst>`_
    - `Standard postgres SQL table <https://github.com/gmalt/api/blob/master/doc/storage_postgres.rst>`_
    - `Postgis SQL table <https://github.com/gmalt/api/blob/master/doc/storage_postgis.rst>`_
- `Usage <https://github.com/gmalt/api/blob/master/doc/usage.rst>`_


TODO
----

* pass config file in command line argument or option
* implement extract elevation from hgt file in task
* logging in webservice
* update readme
