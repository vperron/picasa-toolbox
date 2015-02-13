# -*- coding: utf-8 -*-

default_settings = {

    'DEBUG': False,

    'PICASA_CLIENT': {
        'DATA_TYPE': 'json',
        'PAGE_SIZE': 10,
    }
}


class Settings(object):
    """
    Generate settings object from a default dictionary.
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

settings = Settings(**default_settings)
