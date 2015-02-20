# -*- coding: utf-8 -*-

from datetime import datetime

from .path import fastwalk


TAG_DATETIME = 'Image DateTime'  # actually is DateTimeOriginal it seems.


def iso8601str2datetime(s):
    if s:
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
    return None


def count_files(path):
    num_files = 0
    for x in fastwalk(path, deep=True):
        num_files += 1
    return num_files


def directory2album(name):
    return None if name == '.' else name


def parse_exif_time(tags):
    tag = tags.get(TAG_DATETIME, None)
    if not tag:
        return None
    return datetime.strptime(str(tag), "%Y:%m:%d %H:%M:%S")
