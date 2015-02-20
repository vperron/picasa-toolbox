# -*- coding: utf-8 -*-

from datetime import datetime

TAG_WIDTH = 'EXIF ExifImageWidth'
TAG_HEIGHT = 'EXIF ExifImageLength'
TAG_DATETIME = 'Image DateTime'

def parse_time(tags):
    tag = tags.get(TAG_DATETIME, None)
    if not tag:
        raise KeyError(TAG_DATETIME)
    return datetime.strptime(str(tag), "%Y:%m:%d %H:%M:%S")


def parse_width(tags):
    tag = tags.get(TAG_WIDTH, None)
    if not tag:
        raise KeyError(TAG_WIDTH)
    return int(str(tag), 10)


def parse_height(tags):
    tag = tags.get(TAG_HEIGHT, None)
    if not tag:
        raise KeyError(TAG_HEIGHT)
    return int(str(tag), 10)
