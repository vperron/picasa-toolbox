# -*- coding: utf-8 -*-

import click

from collections import defaultdict

from plusphotos import inspect_dir, list_albums
from plusphotos.settings import Settings


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    if not ctx.obj:
        ctx.obj = Settings()
    ctx.obj.DEBUG = debug


@cli.command(help='WARNING: deprecated.')
@click.argument('path')
@click.pass_context
@click.option('--good', is_flag=True, help='Only list images bearing valid tags.')
@click.option('--bad', is_flag=True, help='Only list images not bearing tags.')
def list_files(ctx, path, good, bad):
    for img in inspect_dir(path):
        if good and not bad and not img.has_exif:
            continue
        if bad and not good and img.has_exif:
            continue

        print img.path, img.album, img.has_exif, img.time


@cli.command()
@click.argument('path')
@click.pass_context
def analyze(ctx, path):
    n_pictures_total = 0
    n_pictures_good = 0
    n_albums = 0  # XXX: warning with 'conflicting' albums, ex: foo/album/x.jpg, bar/album/y.jpg

    pictures = {}
    duplicates_hashes = set()
    albums = defaultdict(list)

    for img in inspect_dir(path):
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
@click.pass_context
def listalbums(ctx):
    list_albums()
