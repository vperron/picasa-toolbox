# -*- coding: utf-8 -*-

"""Base source file for plusphotos

Contains imported public functions.

"""

from scandir import scandir

from .utils import is_jpeg, get_tags
from .tags import parse_time, parse_width, parse_height, parse_orientation


class MetaImage(object):

    def __init__(self, path, tags=None):
        self.path = path
        self.has_exif = False
        if tags:
            try:
                self.time = parse_time(tags)
                self.width = parse_width(tags)
                self.height = parse_height(tags)
                self.orientation = parse_orientation(tags)
                self.has_exif = True
            except KeyError:
                pass  # one of the tags was invalid

    def __repr__(self):
        if self.has_exif:
            return "{path}, [T/W/H/O] = {time}, {width}, {height}, {orientation}".format(
                path=self.path, time=self.time, width=self.width, height=self.height,
                orientation=self.orientation)
        return self.path

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()


def inspect_dir(path, follow_symlinks=False):
    """
    Walks down a path, yield MetaImage objects.
    Only supports JPEG format for now.
    """
    for e in scandir(path):
        if e.is_symlink() and not follow_symlinks:
            continue
        if not e.is_file():
            continue
        if not is_jpeg(e.path):
            continue

        yield MetaImage(e.name, get_tags(e.path))
