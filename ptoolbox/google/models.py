# -*- coding: utf-8 -*-

from peewee import (Model, SqliteDatabase, CharField, IntegerField,
                    DateTimeField, ForeignKeyField, CompositeKey)

from .utils import g_json_key, g_json_value, iso8601str2datetime, ts2dt

db = SqliteDatabase(None)  # Un-initialized database.


class BaseModel(Model):

    class Meta:
        database = db


class GoogleAlbum(BaseModel):
    """Contains methods and accessors to Google Album BaseModels.
    """

    id = CharField(primary_key=True)
    name = CharField()
    title = CharField()
    author = CharField()
    access = CharField()
    summary = CharField()
    num_photos = IntegerField()
    updated = DateTimeField()
    published = DateTimeField()

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
        return GoogleAlbum(**res)


class GooglePhoto(BaseModel):
    """Contains methods and accessors to Google Photo models."""

    album = ForeignKeyField(GoogleAlbum, related_name='photos')
    uuid = CharField()
    url = CharField()
    time = DateTimeField()
    size = IntegerField()
    title = CharField()
    width = IntegerField()
    height = IntegerField()

    class Meta:
        primary_key = CompositeKey('album', 'uuid')

    @classmethod
    def from_raw_json(cls, raw):
        media_group = raw[g_json_key('group', 'media')]
        media_content = media_group[g_json_key('content', 'media')][0]
        res = {
            'uuid': g_json_value(raw, 'id', 'gphoto'),
            'url': media_content['url'],
            'time': ts2dt(int(g_json_value(raw, 'timestamp', 'gphoto')), millisecs=True),
            'size': int(g_json_value(raw, 'size', 'gphoto')),
            'title': g_json_value(raw, 'title'),
            'width': int(g_json_value(raw, 'width', 'gphoto')),
            'height': int(g_json_value(raw, 'height', 'gphoto')),
            'album': g_json_value(raw, 'albumid', 'gphoto'),
        }
        return GooglePhoto(**res)


def init_database(name, reset=False):
    db.init(name)
    db.connect()
    if reset:
        db.drop_tables([GoogleAlbum, GooglePhoto])
        db.create_tables([GoogleAlbum, GooglePhoto])


def close_database(name):
    db.close()
