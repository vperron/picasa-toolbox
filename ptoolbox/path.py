# -*- coding: utf-8 -*-

"""
Contains all file manipulation primitives.

"""

import os
import struct
import imghdr
import hashlib
import exifread

from scandir import scandir

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


def fastwalk(path, deep=True):
    """
    Quickly yields files from the given directory
    """
    for e in scandir(path):
        if deep and e.is_dir():
            # XXX: Python 2 syntax, in python3 use 'yield from'
            for item in fastwalk(e.path, deep):
                yield item
        if not e.is_file():
            continue
        yield(e)


def md5sum(filename, blocksize=65536):
    h = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), ''):
            h.update(block)
    return h.hexdigest()


def jpeg_size(path):
    """Get image size.
    Structure of JPEG file is:
        ffd8 [ffXX SSSS DD DD ...] [ffYY SSSS DDDD ...]  (S is 16bit size, D the data)
    We look for the SOF0 header 0xffc0; its structure is
       [ffc0 SSSS PPHH HHWW ...] where PP is 8bit precision, HHHH 16bit height, WWWW width
    """
    with open(path, 'rb') as f:
        _, header_type, size = struct.unpack('>HHH', f.read(6))
        while header_type != 0xffc0:
            f.seek(size - 2, 1)
            header_type, size = struct.unpack('>HH', f.read(4))
        bpi, height, width = struct.unpack('>BHH', f.read(5))
    return width, height
