# -*- coding: utf-8 -*-
#
# (c) 2016 Jonathan Bouzekri
#
# This file is part of the gMalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/fs-service/master/LICENSE

import glob
import math
import os.path

import gmalthgtparser


class Handler(object):
    TYPE = 'file'

    spec = {
        'folder': 'string()'
    }

    def __init__(self, folder):
        self._validate_folder(folder)
        self.folder = folder

    def get_altitude(self, lat, lng):
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
        lat = int(math.floor(pos[0]))
        lng = int(math.floor(pos[1]))
        return '{}{:02d}{}{:03d}.hgt'.format('N' if lat >= 0 else 'S', lat,
                                             'E' if lng >= 0 else 'W', lng)

    @staticmethod
    def _validate_folder(folder):
        if not os.path.isdir(folder):
            raise Exception('folder {} does not exists '
                            'or is not a directory'.format(folder))

        if not glob.glob(os.path.join(folder, '*.hgt')):
            raise Exception('folder {} does not contain '
                            'any HGT file'.format(folder))
