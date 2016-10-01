# gMalt File Service

gMalt service using data from HGT files directly.

**IMPORTANT:** this version of the gMalt service uses the HGT file directly to find the requested altitude. So on each request, it opens a file. It can be used for site with small load or for testing purpose. For production, I recommend to use the [database service](http://github.com/gmalt/dbservice) version.

## Installation

TODO

## Usage

TODO

## TODO

* pass config file in command line argument or option
* configure folder to find HGT file
* implement extract elevation from hgt file in task
* manage error in webservice
* get coordinates from GET params
* logging in webservice
* update readme
