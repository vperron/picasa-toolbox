# -*- coding: utf-8 -*-

from .path import fastwalk


def count_files(path):
    num_files = 0
    for x in fastwalk(path, deep=True):
        num_files += 1
    return num_files


def directory2album(name):
    return None if name == '.' else name
