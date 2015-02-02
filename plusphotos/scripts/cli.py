# Skeleton of a CLI

import click

import plusphotos


@click.command('plusphotos')
@click.argument('count', type=int, metavar='N')
def cli(count):
    """Echo a value `N` number of times"""
    for i in range(count):
        click.echo(plusphotos.has_legs)
