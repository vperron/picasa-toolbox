# -*- coding: utf-8 -*-

from .path import get_filename, get_dirname
from .utils import directory2album, parse_exif_time


ACCESS_PRIVATE = 'private'


class GoogleAlbum(object):
    """Contains methods and accessors to Google Album objects.
    """

    def __init__(self, id, name, title, author, access, summary, updated, published):
        self.id = id
        self.name = name
        self.title = title
        self.author = author
        self.access = access
        self.summary = summary
        self.updated = updated
        self.published = published


class GooglePhoto(object):
    """Contains methods and accessors to Google Photo objects.
    """

    def __init__(self, id, time, title, album_id, summary, width, height):
        self.id = id
        self.time = time
        self.title = title
        self.width = width
        self.height = height
        self.summary = summary
        self.album_id = album_id


class ImageInfo(object):
    """Contains path to an image, along with a normalized name,
    directory, album title...
    """

    def __init__(self, path, width, height, checksum, time=None, rel_path=None):
        self.path = path
        self.time = time
        self.checksum = checksum
        self.name = get_filename(path)
        self.directory = get_dirname(path)
        self.album_title = directory2album(get_dirname(rel_path if rel_path else path))
        self.width, self.height = width, height

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()
