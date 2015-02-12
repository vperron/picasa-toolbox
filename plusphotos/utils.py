# -*- coding: utf-8 -*-

import imghdr
import exifread


IMGHDR_JPEG_TYPE = 'jpeg'


def is_jpeg(path):
    return imghdr.what(path) == IMGHDR_JPEG_TYPE


def get_tags(path, details=False):
    tags = None
    with open(path, 'rb') as f:
        tags = exifread.process_file(f, details=details)
    return tags
