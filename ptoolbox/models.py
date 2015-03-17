# -*- coding: utf-8 -*-

from .path import get_filename, get_dirname


def directory2album(name):
    return None if name == '.' else name


class ImageInfo(object):
    """Contains path to an image, along with a normalized name,
    directory, album title...
    """

    def __init__(self, path, width, height, checksum, time=None, unique_id=None, rel_path=None):
        self.path = path
        self.time = time
        self.unique_id = unique_id
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
