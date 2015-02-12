# -*- coding: utf-8 -*-

import click

from plusphotos import inspect_dir
from plusphotos.settings import Settings


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    if not ctx.obj:
        ctx.obj = Settings()
    ctx.obj.DEBUG = debug


@cli.command()
@click.argument('path')
@click.pass_context
@click.option('--good', is_flag=True, help='Only list images bearing valid tags.')
@click.option('--bad', is_flag=True, help='Only list images not bearing tags.')
def list(ctx, path, good, bad):
    for img in inspect_dir(path):
        if good and not bad and not img.has_exif:
            continue
        if bad and not good and img.has_exif:
            continue

        print img
