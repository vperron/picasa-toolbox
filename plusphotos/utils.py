# -*- coding: utf-8 -*-

import os
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


def get_filename(path):
    return os.path.basename(path)


def get_dirname(path):
    name = os.path.basename(os.path.dirname(path))
    return '.' if not name else name


def directory2album(name):
    return None if name == '.' else name
