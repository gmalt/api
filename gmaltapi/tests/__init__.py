# -*- coding: utf-8 -*-
#
# (c) 2017 Jonathan Bouzekri
#
# This file is part of the gmalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/api/master/LICENSE.txt

""" Common tools for unit and e2e tests """

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class ResetStingIO(StringIO):
    """ A class to ease test. It provides an implementation of
    StringIO that reset the buffer pointer after each read
    """
    def read(self, *args, **kwargs):
        read_value = StringIO.read(self, *args, **kwargs)
        self.seek(0)
        return read_value
