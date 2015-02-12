# -*- coding: utf-8 -*-

from dateutil import parser

TAG_WIDTH = 'EXIF ExifImageWidth'
TAG_HEIGHT = 'EXIF ExifImageLength'
TAG_DATETIME = 'Image DateTime'
TAG_ORIENTATION = 'Image Orientation'

# XXX: this is a terrible way to retrieve the orientations. Exifread regretfully does not
# get back raw EXIF orientations, and no other library is available on pip as of today.
ORIENTATIONS = [
    'Horizontal (normal)',
    'Mirrored horizontal',
    'Rotated 180',
    'Mirrored vertical',
    'Mirrored horizontal then rotated 90 CCW',
    'Rotated 90 CCW',
    'Mirrored horizontal then rotated 90 CW',
    'Rotated 90 CW',
]


def parse_time(tags):
    tag = tags.get(TAG_DATETIME, None)
    if not tag:
        raise KeyError(TAG_DATETIME)
    return parser.parse(str(tag))  # never raises


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


def parse_orientation(tags):
    tag = tags.get(TAG_ORIENTATION, None)
    if not tag:
        raise KeyError(TAG_ORIENTATION)
    return ORIENTATIONS.index(str(tag)) + 1  # XXX: convert back to original EXIF orientation
