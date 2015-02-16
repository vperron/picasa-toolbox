# -*- coding: utf-8 -*-

import click
import logging

from collections import defaultdict

from plusphotos import list_albums, list_meta_images, log

from .conf import settings
from .utils import count_files


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    settings.DEBUG = debug
    if debug:
        log.setLevel(logging.DEBUG)


@cli.command()
@click.argument('path')
def list_folder(path):
    for img in list_meta_images(path, deep=True):
        print img.name


@cli.command()
@click.argument('path')
def analyze(path):

    # very quickly retrieve the number of files to process
    num_files = count_files(path)
    print "NUM FILES", num_files

    # init analysis
    n_pictures_total = 0
    n_pictures_good = 0
    n_albums = 0  # XXX: warning with 'conflicting' albums, ex: foo/album/x.jpg, bar/album/y.jpg

    pictures = {}
    duplicates_hashes = set()
    albums = defaultdict(list)

    for img in list_meta_images(path, deep=True):
        n_pictures_total += 1
        # implements double picture detection
        if img.checksum in pictures:
            duplicates_hashes.add(img.checksum)
            pictures[img.checksum].append(img)
        else:
            pictures[img.checksum] = [img]
        # eventually add picture to album (must have EXIF)
        if img.has_exif:
            albums[img.album].append(img)
            n_pictures_good += 1

    print '> processed\n\t%d total images\n\t%d with valid EXIF\n\t%d duplicates' % (
        n_pictures_total, n_pictures_good, len(duplicates_hashes))
    print '---- albums'
    for k, v in albums.iteritems():
        print '%s: %d images' % (k, len(v))
    print '---- double images'
    for h in duplicates_hashes:
        print h
        for img in pictures[h]:
            print '\t', img.path


@cli.command('list_albums')
@click.option('--email', prompt='Your email')
@click.option('--password', prompt=True, hide_input=True)
def listalbums(email, password):
    list_albums(email, password)
