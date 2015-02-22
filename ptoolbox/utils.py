# -*- coding: utf-8 -*-

import os

from datetime import datetime

from .path import fastwalk, get_tags, jpeg_size, is_jpeg, md5sum
from .models import ImageInfo


TAG_DATETIME = 'Image DateTime'  # actually is DateTimeOriginal it seems.


def count_files(path):
    num_files = 0
    for x in fastwalk(path, deep=True):
        num_files += 1
    return num_files


def parse_exif_time(tags):
    tag = tags.get(TAG_DATETIME, None)
    if not tag:
        return None
    return datetime.strptime(str(tag), "%Y:%m:%d %H:%M:%S")


def list_valid_images(path, deep=True):
    """Walks down a path, yields ImageInfo objects for every 'valid' image.
    A 'valid' image is any file that is JPEG, has minimum info (width, height)
    Time is optional and may be None.
    """
    for e in fastwalk(path, deep):
        if not is_jpeg(e.path):
            continue
        rel_path = os.path.relpath(e.path, path)
        md5 = md5sum(e.path)
        tags = get_tags(e.path)
        time = parse_exif_time(tags)
        try:
            width, height = jpeg_size(e.path)
        except ValueError, e:
            continue
        img = ImageInfo(e.path, width, height, md5, time, rel_path=rel_path)
        yield img
