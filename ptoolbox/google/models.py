# -*- coding: utf-8 -*-

from .utils import g_json_key, g_json_value, iso8601str2datetime, ts2dt


class GoogleAlbum(object):
    """Contains methods and accessors to Google Album objects.
    """

    def __init__(self, id, name, title, author, access, summary, updated, published, num_photos):
        self.id = id
        self.name = name
        self.title = title
        self.author = author
        self.access = access
        self.summary = summary
        self.updated = updated
        self.published = published
        self.num_photos = num_photos

    @classmethod
    def from_raw_json(cls, raw):
        res = {
            'id': g_json_value(raw, 'id', 'gphoto'),
            'title': g_json_value(raw, 'title'),  # original title, may create doubles
            'name': g_json_value(raw, 'name', 'gphoto'),  # camel-cased unique name identifier
            'author': g_json_value(raw['author'][0], 'name'),
            'access': g_json_value(raw, 'access', 'gphoto'),
            'summary': g_json_value(raw, 'summary'),
            'updated': iso8601str2datetime(g_json_value(raw, 'updated')),
            'published': iso8601str2datetime(g_json_value(raw, 'published')),
            'num_photos': int(g_json_value(raw, 'numphotos', 'gphoto')),
        }
        return cls(**res)


class GooglePhoto(object):
    """Contains methods and accessors to Google Photo objects.
    """

    def __init__(self, id, url, size, time, title, album_id, width, height):
        self.id = id
        self.url = url
        self.size = size
        self.time = time
        self.title = title
        self.width = width
        self.height = height
        self.album_id = album_id

    @classmethod
    def from_raw_json(cls, raw):
        media_group = raw[g_json_key('group', 'media')]
        media_content = media_group[g_json_key('content', 'media')][0]
        res = {
            'id': g_json_value(raw, 'id', 'gphoto'),
            'url': media_content['url'],
            'time': ts2dt(int(g_json_value(raw, 'timestamp', 'gphoto')), millisecs=True),
            'size': int(g_json_value(raw, 'size', 'gphoto')),
            'title': g_json_value(raw, 'title'),
            'width': int(g_json_value(raw, 'width', 'gphoto')),
            'height': int(g_json_value(raw, 'height', 'gphoto')),
            'album_id': g_json_value(raw, 'albumid', 'gphoto'),
        }
        return cls(**res)
