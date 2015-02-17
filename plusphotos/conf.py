# -*- coding: utf-8 -*-


""" Define what happens when a picture does not get auto album name from folder"""
ALBUM_STRATEGY_ASK = 'ask'  # ask the user for a default name
ALBUM_STRATEGY_USE_DEFAULT = 'default'  # use default album name


default_settings = {

    'DEBUG': False,

    'DEFAULT_ALBUM': 'ptoolbox',
    'ALBUM_STRATEGY': ALBUM_STRATEGY_USE_DEFAULT,

    'PICASA_CLIENT': {
        'DATA_TYPE': 'json',
        'PAGE_SIZE': 50,
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
