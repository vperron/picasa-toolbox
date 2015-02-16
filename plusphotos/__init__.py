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

from .api import PicasaClient
from .models import ImageInfo
from .path import get_tags, is_jpeg, md5sum
from .utils import fastwalk


def list_meta_images(path, deep=True):
    """Walks down a path, yields MetaImage objects.
    Only supports JPEG format for now.
    """
    for e in fastwalk(path, deep):
        if not is_jpeg(e.path):
            continue
        try:
            img = ImageInfo(e.path, md5sum(e.path), get_tags(e.path))
            yield img
        except KeyError, ValueError:
            continue


def list_albums(login, password):
    p = PicasaClient()
    p.authenticate(login, password)
    for x in p.fetch_albums():
        print "%s - '%s' (%s)" % (x.published.isoformat(), x.title, x.author)


def sync_image(path, warn=True, resize=True):
    """Synchronizes an image with a remote album on Google+.
    """
    pass
