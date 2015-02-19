# -*- coding: utf-8 -*-

"""CLI features. We can expect functions that ask for user input,
have side effects and are heavily procedural here: it's OK.
"""

import click
import logging

from collections import defaultdict

from ptoolbox import log, list_valid_images, upload_folder

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
def analyze(path):

    # efficiently retrieve the number of files to process (first fast pass)
    num_files = count_files(path)

    # init analysis
    n_pictures_total = 0
    n_pictures_good = 0
    n_pictures_orphan = 0
    n_albums = 0  # XXX: may get 'conflicting' albums, ex: foo/album/x.jpg, bar/album/y.jpg

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
        if not img.album_title:
            n_pictures_orphan += 1

        # eventually add picture to album
        if img.is_valid and img.album_title:
            albums[img.album_title].append(img)
            n_pictures_good += 1

    log.info('> processed\n\t%d total images\n\t%d valid images\n\t%d orphan images\n\t%d duplicates' % (
        n_pictures_total, n_pictures_good, n_pictures_orphan, len(duplicates_hashes)))
    log.info('---- albums')
    for k, v in albums.iteritems():
        log.info('%s: %d images' % (k, len(v)))
    log.info('---- double images')
    for h in duplicates_hashes:
        log.info("hash: '%s'" % h)
        for img in pictures[h]:
            log.info('\t%s' % img.path)


@cli.command('list_albums')
@click.option('--email', prompt='Your email')
@click.option('--password', prompt=True, hide_input=True)
def listalbums(email, password):
    p = PicasaClient()
    p.authenticate(email, password)
    for album in p.fetch_albums():
        print "%s - '%s' [%s-%s] (%s)" % (
            album.published.isoformat(), album.id, album.title, album.name, album.author)


@cli.command('delete_album')
@click.option('--email', prompt='Your email')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--force', is_flag=True)
@click.argument('title')
def deletealbum(email, password, force, title):
    p = PicasaClient()
    p.authenticate(email, password)
    for album in p.fetch_albums():
        if title.lower() in album.name.lower():
            if force or click.confirm("Delete you want to delete album '%s'?" % album.title):
                p.delete_album(album.id)
                log.info("Deleted album '%s'." % album.title)


@cli.command('upload_folder')
@click.option('--email', prompt='Your email')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--default_album', default=None, hide_input=True,
              help='As a default, images without an album aren\'t uploaded. This sets a default one.')
@click.argument('path')
def uploadfolder(email, password, default_album, path):
    p = PicasaClient()
    p.authenticate(email, password)
    if default_album:
        settings.DEFAULT_ALBUM = default_album
    upload_folder(p, path)
