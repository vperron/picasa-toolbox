# -*- coding: utf-8 -*-

import click

from plusphotos import inspect_dir


@click.command('plusphotos')
@click.argument('path')
@click.option('--good', is_flag=True, default=False)
@click.option('--bad', is_flag=True, default=False)
def cli(path, good, bad):
    for img in inspect_dir(path):
        if good and not bad and not img.has_exif:
            continue

        if bad and not good and img.has_exif:
            continue

        print img
