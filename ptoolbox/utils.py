# -*- coding: utf-8 -*-

from datetime import datetime

from .path import fastwalk


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
