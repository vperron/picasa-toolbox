# -*- coding: utf-8 -*-

"""CLI features. We can expect functions that ask for user input,
have side effects and are heavily procedural here: it's OK.
"""

from __future__ import print_function

import click
import logging
import os
import os.path
import sys

from collections import defaultdict

from ptoolbox import log

from .conf import settings
from .google import picasa_client as pc, utils, models
from .path import ptoolbox_dir, ensure_directory, download_file
from .utils import count_files, list_valid_images, dt2str


def init_user_database(login, reset=False):
    """Inits the SQLite database for the given user"""
    ensure_directory(ptoolbox_dir)
    db_file_path = os.path.join(ptoolbox_dir, '%s.db' % login)
    models.init_database(db_file_path, reset)


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    settings.DEBUG = debug
    if debug:
        log.setLevel(logging.DEBUG)


@cli.command('init')
@click.argument('login')
@click.option('--password', prompt=True, hide_input=True)
def init(login, password):
    """Creates a $HOME/.ptoolbox/<login>.db containing a SQLite
    database of all pictures & albums for <login>.
    """
    init_user_database(utils.mail2username(login), reset=True)
    pc.authenticate(login, password)

    print("fetching all albums... ", end='')
    n_albums = 0
    for album in pc.fetch_albums():
        album.save(force_insert=True)
        n_albums += 1
    print("done.")

    index = 1
    for album in models.GoogleAlbum.select():
        print("album %03d of %03d: '%s', %d pictures" % (index, n_albums, album.title, album.num_photos))
        for photo in pc.fetch_images(album.id):
            print('.', end='')
            sys.stdout.flush()
            photo.save(force_insert=True)
        index += 1
        print('\n')

    models.db.close()


@cli.command('sync')
@click.argument('login')
@click.argument('path')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--preinit/--no-preinit', default=True)
def sync(login, path, password, preinit):
    """Synchronizes the <login> Google+ Photos account with a
    local folder in <path>.
    Procedure:
        - Downloads every remote picture that isn't matched by a local one
        - Uploads every picture that doesn't exist online.
    The default behaviour is to create an offline folder for
    every online album.
    Pictures in <path> are deep-located and moved to their root
    album directory if needed.
    """
    if preinit:
        init(login, password)
    else:
        init_user_database(utils.mail2username(login))

    for img in list_valid_images(path, deep=True):
        if img.time == None:
            continue  # ignore images that have no time, pollutes online album. Move them ?
        try:
            qs = models.GooglePhoto.select().where(models.GooglePhoto.time == img.time)
            print("SELECT TIME", img.name, img.time, qs.count())
        except models.GooglePhoto.DoesNotExist as e:
            # upload it
            print('must upload %s' % img.name)
            pass

    # # TODO: make a first pass to check how many we'll be downloading,
    # # conflicts, etc. THEN, synchronize. Also enables --dry-run flags !
    # for album in models.GoogleAlbum.select():
    #     album_path = os.path.join(path, album.name)
    #     ensure_directory(album_path)
    #     for img in album.photos:
    #         img_filename = '%s.jpg' % (img.time.strftime('%Y-%m-%dT%H%M%S'), )
    #         img_path = os.path.join(album_path, img_filename)
    #         if not os.path.exists(img_path):
    #             download_file(img.url, img_path)
    #             print("> downloaded: img '%s'" % (img_filename,))
    #         else:
    #             print("> exists: img '%s'" % (img_filename,))
    # pass


@cli.command('flatten')
@click.argument('login')
@click.argument('path')
def flatten(login, path):
    pass


@cli.command('unflatten')
@click.argument('login')
@click.argument('path')
def unflatten(login, path):
    pass
