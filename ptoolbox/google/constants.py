# -*- coding: utf-8 -*-

from datetime import datetime

epoch = datetime.utcfromtimestamp(0)

ACCESS_PRIVATE = 'private'

G_XML_ROOT = 'root'  # any identifier really; as long as it's not hardcoded

G_XML_NAMESPACES = {
    G_XML_ROOT: 'http://www.w3.org/2005/Atom',
    'gd': 'http://schemas.google.com/g/2005',
    'app': 'http://www.w3.org/2007/app',
    'gdata': 'http://www.w3.org/2005/Atom',
    'gphoto': 'http://schemas.google.com/photos/2007',
    'media': 'http://search.yahoo.com/mrss/',
}

ALBUM_FIELDS = ','.join((
    'gphoto:id', 'gphoto:name', 'author', 'gphoto:access', 'summary',
    'title', 'updated', 'published'))

PHOTO_FIELDS = ','.join((
    'gphoto:id', 'gphoto:timestamp', 'title', 'gphoto:albumid', 'summary',
    'gphoto:width', 'gphoto:height', 'exif:tags'))
