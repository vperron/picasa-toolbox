# -*- coding: utf-8 -*-

import re
import requests

from .conf import settings
from .utils import iso8601str2datetime
from .models import GoogleAlbum


def gvalue(data, key, prefix=None):
    """Returns a google-encoded value from the feed. Example:
        json = {"gphoto$access": { "$t": "private" }}
        gvalue(json, 'access', 'gphoto') = 'private'
    """
    key = key if prefix is None else '%s$%s' % (prefix, key)
    return data[key]['$t']


def raw2album(raw):
    """Returns a GoogleAlbum object from the raw JSON data.
    """
    res = {
        'title': gvalue(raw, 'title'),
        'author': gvalue(raw['author'][0], 'name'),
        'rights': gvalue(raw, 'rights'),
        'summary': gvalue(raw, 'summary'),
        'updated': iso8601str2datetime(gvalue(raw, 'updated')),
        'published': iso8601str2datetime(gvalue(raw, 'published')),
    }
    return GoogleAlbum(**res)


class PicasaClient(object):

    PWA_SERVICE = 'lh2'  # internal service name for Picasa Web API
    AUTH_URL = 'https://www.google.com/accounts/ClientLogin'

    def __init__(self, data_type=None, page_size=None):
        self.token = None
        self.login = None
        self.password = None
        self.data_type = data_type
        self.page_size = page_size
        if data_type is None:
            self.data_type = settings.PICASA_CLIENT['DATA_TYPE']
        if page_size is None:
            self.page_size = settings.PICASA_CLIENT['PAGE_SIZE']

    def authenticate(self, login, password):
        login = login.split('@')[0]  # remove the e-mail part of the login
        self.login = login
        self.password = password
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        params = {'Email': login, 'Passwd': password, 'service': self.PWA_SERVICE}
        res = requests.post(self.AUTH_URL, params=params, headers=headers)
        if res.status_code != 200:
            raise ValueError('authentication failed.')
        match = re.search('Auth=(\S*)', res.text)
        if not match:
            raise ValueError('unexpected authentication error: invalid answer.')
        self.token = match.group(1)

    def _url(self):
        return 'https://picasaweb.google.com/data/feed/api/user/%s' % self.login

    def _headers(self):
        return {
            'Content-Type': 'application/atom+xml',
            'Authorization': 'GoogleLogin auth=%s' % self.token
        }

    def _params(self, kind, page_size, index=1):
        return {
            'alt': self.data_type,
            'kind': kind,
            'max-results': page_size,
            'start-index': index,
        }

    def fetch_albums(self, page_size=None, index=1):
        if page_size is None:
            page_size = self.page_size
        params = self._params('album', page_size=page_size, index=index)
        res = requests.get(self._url(), params=params, headers=self._headers())
        if res.status_code != 200:
            raise ValueError('could not fetch web albums')
        data = res.json()['feed']
        for album in data['entry']:
            yield raw2album(album)
        total_results = gvalue(data, 'totalResults', 'openSearch')
        remaining_results = total_results - (index + page_size - 1)
        if remaining_results > 0:
            for item in self.fetch_albums(page_size, index + page_size):
                yield item
