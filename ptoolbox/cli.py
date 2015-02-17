# -*- coding: utf-8 -*-

"""CLI features. We can expect functions that ask for user input,
have side effects and are heavily procedural here: it's OK.
"""

import click
import logging

from collections import defaultdict

from ptoolbox import list_valid_images, sync_folder, log

from .api import PicasaClient
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
    for img in list_valid_images(path, deep=True):
        print img.name


@cli.command()
@click.argument('path')
def analyze(path):

    # efficiently retrieve the number of files to process (first fast pass)
    num_files = count_files(path)

    # init analysis
    n_pictures_total = 0
    n_pictures_good = 0
    n_albums = 0  # XXX: warning with 'conflicting' albums, ex: foo/album/x.jpg, bar/album/y.jpg

    pictures = {}
    duplicates_hashes = set()
    albums = defaultdict(list)

    for img in list_valid_images(path, deep=True):
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
    p = PicasaClient()
    p.authenticate(email, password)
    for album in p.fetch_albums():
        print "%s - '%s' (%s)" % (album.published.isoformat(), album.title, album.author)


@cli.command('sync_folder')
@click.option('--email', prompt='Your email')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--default_album', default=None, hide_input=True)
@click.argument('path')
def syncfolder(email, password, default_album, path):
    p = PicasaClient()
    p.authenticate(email, password)
    if default_album:
        settings.DEFAULT_ALBUM = default_album
    sync_folder(p, path)