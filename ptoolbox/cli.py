# -*- coding: utf-8 -*-

"""CLI features. We can expect functions that ask for user input,
have side effects and are heavily procedural here: it's OK.
"""

import os
import click
import logging

from collections import defaultdict

from ptoolbox import log

from .conf import settings
from .utils import count_files, list_valid_images
from .google import PicasaClient


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
        print img.name, img.width, img.time

        # implements double picture detection
        if img.checksum in pictures:
            duplicates_hashes.add(img.checksum)
            pictures[img.checksum].append(img)
        else:
            pictures[img.checksum] = [img]
        if not img.album_title:
            n_pictures_orphan += 1

        # eventually add picture to album
        if img.time and img.album_title:
            albums[img.album_title].append(img)
            n_pictures_good += 1

    print '> processed\n\t%d total images\n\t%d valid images\n\t%d orphan images\n\t%d duplicates' % (
        n_pictures_total, n_pictures_good, n_pictures_orphan, len(duplicates_hashes))
    print '---- albums'
    for k, v in albums.iteritems():
        print '%s: %d images' % (k, len(v))
    print '---- double images'
    for h in duplicates_hashes:
        print "hash: '%s'" % h
        for img in pictures[h]:
            print '\t%s' % img.path


@cli.command(help="Flattens valid images from SOURCE to DEST, renaming them opionatedly.")
@click.argument('src_path')
@click.argument('dst_path')  # eventually add --invalid=, --duplicates= ...
def flatten_local(src_path, dst_path):

    # TODO: add file listing in the beginning, how many files to process,
    # possible conflicts, etc.

    for img in list_valid_images(src_path, deep=True):
        if img.time is None:
            continue

        time_str = img.time.strftime('%Y-%m-%dT%H%M%S')
        hash_str = img.checksum[0:4]
        dst_name = '{time}-{hash}.jpg'.format(time=time_str, hash=hash_str)
        dst_full = os.path.join(dst_path, dst_name)
        if os.path.isfile(dst_full):
            # TODO: implement this case (ask the user ? compare the files ? erase ?
            continue
        os.rename(img.path, dst_full)


@cli.command('list_albums')
@click.option('--email', prompt='Your email')
@click.option('--password', prompt=True, hide_input=True)
def listalbums(email, password):
    p = PicasaClient()
    p.authenticate(email, password)
    for album in p.fetch_albums():
        print "%s - '%s' [%s-%s] (%s)" % (
            album.published.isoformat(), album.id, album.title, album.name, album.author)


@cli.command('list_images')
@click.option('--email', prompt='Your email')
@click.option('--password', prompt=True, hide_input=True)
@click.argument('album_id', default='default')
def listimages(email, password, album_id):
    p = PicasaClient()
    p.authenticate(email, password)
    for img in p.fetch_images(album_id):
        print "%s / %s - '%s' [%sx%s]" % (
            img.time.isoformat(), img.id, img.title, img.width, img.height)


@cli.command('get_image')
@click.option('--email', prompt='Your email')
@click.option('--password', prompt=True, hide_input=True)
@click.argument('album_id', default='default')
@click.argument('photo_id')
def listimages(email, password, album_id, photo_id):
    p = PicasaClient()
    p.authenticate(email, password)
    photo = p.get_image(photo_id, album_id)
    print photo.title, photo.url


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
    client = PicasaClient()
    client.authenticate(email, password)
    if default_album:
        settings.DEFAULT_ALBUM = default_album

    log.debug('fetching remote albums...')
    remote_albums = [album for album in client.fetch_albums()]

    # index albums by title
    albums = {album.title: album for album in remote_albums}

    # index image collections by album id
    remote_images = {}

    for img in list_valid_images(path):

        # get or create album from its title (directory name)
        title = img.album_title if img.album_title else settings.DEFAULT_ALBUM
        if title and title in albums.keys():
            album = albums[title]
        else:
            log.debug("creating album '%s'" % title)
            album_id = client.create_album(title)
            album = client.get_album(album_id)

        # fetch list of album images if necessary
        if album.id not in remote_images:
            log.debug("getting list of images for album '%s'" % album.title)
            remote_images[album.id] = [rimg for rimg in client.fetch_images(album.id)]
            for x in remote_images[album.id]:
                log.debug("\tremote %s - '%s' [%dx%d]" % (
                    x.time.isoformat(), x.title, x.width, x.height))

        # upload image
        log.debug("uploading image '%s' from album '%s' [%s]" % (img.name, album.title, album.id))
        # upload_image(client, img, album.id, warn, resize, force_push, remote_images[album.id])

        if remote_images is None:
            remote_images = [rimg for rimg in client.fetch_images(album_id)]

        # if the image does _not_ have a date, ask to continue

        # download all the available images as quickly as possible from the server
        # unless remote is not None but [{album0}, ...]

        # store it internally as a double dictionary: name -> date taken

        # if there's a match, tell that image already exists. force ?

        # if there's a partial match (name or date taken exists), display info
        # about candidate. ask for which one to force.

        # if the image has no album, warn.
