# -*- coding: utf-8 -*-

"""Base source file for picasa-toolbox.
Contains higher-level functions that use API, models and utils.
WARNING: try and be as functional and without side effects as possible !
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

import warnings

from .conf import settings
from .models import ImageInfo
from .path import get_tags, is_jpeg, md5sum
from .utils import fastwalk


def list_valid_images(path, deep=True):
    """Walks down a path, yields ImageInfo objects for every 'valid' image.
    A 'valid' image is any file that is JPEG, has minimum info (width, height)
    """
    for e in fastwalk(path, deep):
        if not is_jpeg(e.path):
            continue
        try:
            img = ImageInfo(e.path, md5sum(e.path), get_tags(e.path))
            yield img
        except KeyError, ValueError:  # we keep
            continue


def sync_image(client, imginfo, album_id, warn=True, resize=True, force_push=False, remote_images=None):
    """Synchronizes an image with a remote album on Google+.
    """
    if remote_images is None:
        remote_images = [rimg for rimg in client.fetch_images(album_id)]

    # if the image does _not_ have a date, ask to continue

    # download all the available images as quickly as possible from the server
    # unless remote is not None but [{album0}, ...]

    # store it internally as a double dictionary: name -> date taken

    # if there's a match, tell that image already exists. force ?

    # if there's a partial match (name or date taken exists), display info
    # about candidate. ask for which one to force.

    # if the image has no album, warn.
    pass


def sync_folder(client, path, warn=True, resize=True, force_push=False, remote_albums=None):
    """Synchronizes a whole folder on Google+ Photos.
    """
    if remote_albums is None:
        log.debug('fetching remote albums...')
        remote_albums = [album for album in client.fetch_albums()]

    # index albums by title
    albums = {album.title: album for album in remote_albums}

    # index image collections by album id
    remote_images = {}

    for img in list_valid_images(path):
        title = img.album_title if img.album_title else settings.DEFAULT_ALBUM
        if title in albums.keys():
            album = albums[title]
        else:
            # create the album ? ask for what to do ? stop here ?
            # maybe the best option would be to list local & remote albums
            # first, arn about differences and only sync already present ?
            continue
            raise NotImplementedError
        log.debug("sync image '%s' from album '%s' [%s]" % (img.name, album.title, album.id))
        if album.id not in remote_images:
            remote_images[album.id] = [rimg for rimg in client.fetch_images(album.id)]
            for x in remote_images[album.id]:
                log.debug("\tremote %s - '%s' [%dx%d]" % (
                    x.time.isoformat(), x.title, x.width, x.height))
        sync_image(client, img, album.id, warn, resize, force_push, remote_images[album.id])
