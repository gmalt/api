import random


print('file handler module loaded')

class Handler(object):
    TYPE = 'file'

    spec = {
        'folder': 'string()'
    }

    def __init__(self, folder):
        self.folder = folder

    def get_altitude(self, lat, lng):
        print('finding altitude with POS({}, {})'.format(lat, lng))
        return random.randint(0, 100)
