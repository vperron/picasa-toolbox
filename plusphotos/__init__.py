# -*- coding: utf-8 -*-

"""Base source file for plusphotos

Contains imported public functions.

"""

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())  # TODO: use a real logging config

from .tags import parse_time, parse_width, parse_height, parse_orientation
from .path import (get_tags, is_jpeg, get_filename, get_dirname, md5sum)
from .utils import directory2album, fastwalk


class MetaImage(object):

    def __init__(self, path, checksum, tags=None):
        self.path = path
        self.checksum = checksum
        self.name = get_filename(path)
        self.directory = get_dirname(path)
        self.album = directory2album(self.directory)
        self.has_exif = False
        if tags:
            try:
                self.time = parse_time(tags)
                self.width = parse_width(tags)
                self.height = parse_height(tags)
                self.orientation = parse_orientation(tags)
                self.has_exif = True
            except KeyError as e:
                log.debug('KeyError: %s' % e)
            except ValueError as e:
                log.debug('ValueError: %s' % e)

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()


def list_meta_images(path, deep=True):
    """
    Walks down a path, yields MetaImage objects.
    Only supports JPEG format for now.
    """
    for e in fastwalk(path, deep):
        if not is_jpeg(e.path):
            continue
        yield MetaImage(e.path, md5sum(e.path), get_tags(e.path))


def list_albums(g_handle):
    pass
