gmalt API - Raw HGT file in the filesystem
==========================================

If you don't have configured the server yet, please read the `Installation <https://github.com/gmalt/api/blob/master/doc/install.rst>`_ documentation

This section describes the ``file`` handler.

This handler opens a SRTM HGT file on each request to find the wanted elevation. As such, it is not very efficient but it is good enough for
demonstration purposes or for really low load services.

It is quite easy to set up.

1. Create a folder somewhere. For example ``/data/srtm3``

2. Install the `gmalt cli <https://github.com/gmalt/cli>`_

3. Run the gmalt cli `gmalt-hgtget <https://github.com/gmalt/cli/blob/master/doc/cli_hgtget.rst>`_

.. code-block:: console

    gmalt-hgtget srtm3 /data/srtm3

This will download all SRTM3 dataset zip files and unzip it in the folder ``/data/srtm3``

4. (Optionaly you can remove the now useless downloaded zip files : ``rm -rf /data/srtm3/*.zip``)

5. Configure the gmalt API :

.. code-block:: ini

    [server]
    handler = file

    [handler]
    folder = /data/srtm3

6. Launch the gmalt API server and start to use the API
