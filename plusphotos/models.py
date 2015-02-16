# -*- coding: utf-8 -*-

from plusphotos import log

from .tags import parse_time, parse_width, parse_height, parse_orientation
from .path import get_filename, get_dirname
from .utils import directory2album


class GoogleAlbum(object):
    """Contains methods and accessors to Google Albums.
    """

    def __init__(self, title, author, rights, summary, updated, published):
        self.title = title
        self.author = author
        self.rights = rights
        self.summary = summary
        self.updated = updated
        self.published = published


class ImageInfo(object):
    """Contains path to an image, along with a normalized name,
    directory, album, and several tags.
    """

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
            except KeyError, ValueError as e:
                pass  # if one tag is faulty, just pass for now.

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

