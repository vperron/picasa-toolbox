# -*- coding: utf-8 -*-

"""Base source file for plusphotos

Contains imported public functions.

"""

from scandir import scandir

from .tags import parse_time, parse_width, parse_height, parse_orientation
from .utils import (is_jpeg, get_tags, get_filename, get_dirname,
                    directory2album, md5sum)


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
            except KeyError:
                pass  # one of the tags was not found
            except ValueError:
                pass  # one of the tag values was invalid

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()


def inspect_dir(path, deep=True, follow_symlinks=False):
    """
    Walks down a path, yield MetaImage objects.
    Only supports JPEG format for now.
    """
    for e in scandir(path):
        if deep and e.is_dir():
            # XXX: Python 2 syntax, in python3 use 'yield from'
            for item in inspect_dir(e.path, deep, follow_symlinks):
                yield item
        if e.is_symlink() and not follow_symlinks:
            continue
        if not e.is_file():
            continue
        if not is_jpeg(e.path):
            continue

        yield MetaImage(e.path, md5sum(e.path), get_tags(e.path))





APP_NAME = 'plusphotos'
from gdata.photos.service import PhotosService

def login(email, password):
    gd_client = PhotosService()  # XXX: no way to init all at once ?
    gd_client.email = 'perron.victor@gmail.com'
    gd_client.password = 'APP_PASSWORD'
    gd_client.source = APP_NAME
    gd_client.ProgrammaticLogin()
    return gd_client


def list_albums(g_handle):
    pass






def sync_image(g_handle, img, resize=True):
    """
    Synchronizes an image with a remote album on Google+.
    """
    pass
