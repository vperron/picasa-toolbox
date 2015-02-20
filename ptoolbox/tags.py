# -*- coding: utf-8 -*-

import struct
from datetime import datetime

TAG_WIDTH = 'EXIF ExifImageWidth'
TAG_HEIGHT = 'EXIF ExifImageLength'
TAG_DATETIME = 'Image DateTime'


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
