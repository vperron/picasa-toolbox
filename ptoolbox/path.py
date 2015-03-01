# -*- coding: utf-8 -*-

"""
Contains all file manipulation primitives.

"""

import exifread
import hashlib
import imghdr
import os
import os.path
import requests
import struct

from scandir import scandir

IMGHDR_JPEG_TYPE = 'jpeg'
PTOOLBOX_BASE_DIR = '.ptoolbox'


home_dir = os.path.expanduser('~')
ptoolbox_dir = os.path.join(home_dir, PTOOLBOX_BASE_DIR)


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


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


def is_jpeg_header(header_type):
    return header_type & 0xff00 == 0xff00


def is_sof0_header(header_type):
    return header_type in (0xffc0, 0xffc1, 0xffc2, 0xffc3)


def jpeg_size(path):
    """Get image size.
    Structure of JPEG file is:
        ffd8 [ffXX SSSS DD DD ...] [ffYY SSSS DDDD ...]  (S is 16bit size, D the data)
    We look for the SOFx header 0xffcx; its structure is
       [ffcx SSSS PPHH HHWW ...] where PP is 8bit precision, HHHH 16bit height, WWWW width
    """
    with open(path, 'rb') as f:
        _, header_type, size = struct.unpack('>HHH', f.read(6))
        while is_jpeg_header(header_type) and not is_sof0_header(header_type):
            f.seek(size - 2, 1)
            header_type, size = struct.unpack('>HH', f.read(4))
        if is_sof0_header(header_type):
            bpi, height, width = struct.unpack('>BHH', f.read(5))
            return width, height
    raise ValueError('the file does not bear a valid SOF0 header')


def download_file(url, filename=None):
    """Downloads a file using its URL; does not accept special headers yet.
    """
    if not filename:
        filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter-out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return filename
