# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Module providing the handler to load elevation date directly
from file on each request. Useful for small project or for quick testing
purpose """

import glob
import math
import os.path

import gmalthgtparser


class Handler(object):
    """ The `file` handler type.
    Providing a `lat` and `lng`, it looks in a specific folder
    for a HGT file and returns the elevation value stored in this
    file for this position

    :param str folder: the folder containing the HGT file
    :raises Exception: if the folder does not exist or it does not
        contain any HGT file
    """
    TYPE = 'file'

    spec = {
        'folder': 'string()'
    }

    def __init__(self, folder):
        self._validate_folder(folder)
        self.folder = folder

    def get_altitude(self, lat, lng):
        """ Load the HGT file that matches the provided `lat` and
        `lng` and returns the elevation value for this position

        :param float lat: the latitude of the elevation you are looking for
        :param float lng: the longitude of the elevation you are looking for
        :return: the elevation value for this position or None if not found
        :rtype: float or None
        """
        pos = (lat, lng)

        hgt_filename = self._hgt_filename_from_coordinates(pos)
        hgt_file = os.path.join(self.folder, hgt_filename)
        if not os.path.isfile(hgt_file):
            # TODO : log file not found lvl DEBUG
            return None

        with gmalthgtparser.HgtParser(hgt_file) as parser:
            alt = parser.get_elevation(pos)

        return alt[2]

    @staticmethod
    def _hgt_filename_from_coordinates(pos):
        """ Get the name of a HGT file where you can find the
        elevation value of the provided position

        :param pos: the position you want the elevation
        :type pos: tuple(float, float) with first value being the lat
        """
        lat = int(math.floor(pos[0]))
        lng = int(math.floor(pos[1]))
        lat_symbol = 'N' if lat >= 0 else 'S'
        lng_symbol = 'E' if lng >= 0 else 'W'
        return '{}{:02d}{}{:03d}.hgt'.format(lat_symbol, abs(lat),
                                             lng_symbol, abs(lng))

    @staticmethod
    def _validate_folder(folder):
        """ Called on handler instanciation for a quick check if the
        provided folder exists and contains file with the `.hgt` ext

        :param str folder: the folder where the handler can find HGT files
        :raises Exception: if the folder does not exist or if the folder
            does not contain any HGT file
        """
        if not os.path.isdir(folder):
            raise Exception('folder {} does not exists '
                            'or is not a directory'.format(folder))

        # TODO : keep a reference to all available HGT files if already loaded
        if not glob.glob(os.path.join(folder, '*.hgt')):
            raise Exception('folder {} does not contain '
                            'any HGT file'.format(folder))
