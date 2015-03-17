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
@click.option('--dry-run/--no-dry-run', default=False)
def init(login, password, dry_run):
    """Creates a $HOME/.ptoolbox/<login>.db containing a SQLite
    database of all pictures & albums for <login>.
    """
    if dry_run:
        db_name = '__tmp__'  # FIXME: this is a hack, would be better that dry_run actually does not write
    else:
        db_name = utils.mail2username(login)

    init_user_database(db_name, reset=True)
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

    # uploads existing images
    for img in list_valid_images(path, deep=True):
        if img.unique_id:
            qs = models.GooglePhoto.select().where(models.GooglePhoto.unique_id == img.unique_id)
            if qs.count() == 1:
                continue
            # img.ensure_time_tag(eventual_replace=now())
            # img.upload()
            # models.GooglePhoto.update(status = STATUS_SYNCED)
            continue

        # if there's no image unique ID in the tags, use the time property.
        if img.time == None:
            print('ignoring %s' % img.name)
            continue  # ignore images that have no time, pollutes online album. Move them ?
        qs = models.GooglePhoto.select().where(models.GooglePhoto.time == img.time)
        cnt = qs.count()
        if cnt == 0:
            # upload it, ensure timestamp both in file and in gphoto:timestamp,
            # mark as synchronized.
            print('must upload %s' % img.name)
            pass
        elif cnt == 1:
            # there's a unique match, mark as synchronized and continue
            continue
        else:
            # more than one match means a conflict. must check later on with
            # the MD5s as uniqueIDs.
            continue

    # downloads missing images (all the ones marked as status != synchronized)

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
    #             ensure_tag_file_date(img_path, img.time)
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
