# -*- coding: utf-8 -*-

"""Implements methods to interact with the Picasa Wweb Albums API 2.0,
cf. https://developers.google.com/picasa-web/docs/2.0/reference
"""

import re
import json
import requests

from datetime import datetime, timedelta

from ptoolbox import log

from .conf import settings
from .utils import iso8601str2datetime
from .models import GoogleAlbum, GooglePhoto


def ts2dt(ts, millisecs=False):
    if millisecs:
        dt = datetime.utcfromtimestamp(ts / 1000)
        return dt + timedelta(milliseconds=ts % 1000)
    return datetime.utcfromtimestamp(ts)


def gvalue(data, key, namespace=None, accessor='$t'):
    """Returns a google-encoded value from the feed. Example:
    json = {"gphoto$access": { "$t": "private" }}, then
    gvalue(json, 'access', 'gphoto') is 'private'
    """
    key = key if namespace is None else '%s$%s' % (namespace, key)
    return data[key][accessor]


def raw2album(raw):
    """Returns a GoogleAlbum object from the raw JSON data.
    """
    res = {
        'id': gvalue(raw, 'id', 'gphoto'),
        'title': gvalue(raw, 'title'),
        'author': gvalue(raw['author'][0], 'name'),
        'rights': gvalue(raw, 'rights'),
        'summary': gvalue(raw, 'summary'),
        'updated': iso8601str2datetime(gvalue(raw, 'updated')),
        'published': iso8601str2datetime(gvalue(raw, 'published')),
    }
    return GoogleAlbum(**res)


def raw2photo(raw):
    """Returns a GoogleAlbum object from the raw JSON data.
    """
    res = {
        'id': gvalue(raw, 'id', 'gphoto'),
        'time': ts2dt(int(gvalue(raw, 'timestamp', 'gphoto')), millisecs=True),
        'title': gvalue(raw, 'title'),
        'width': int(gvalue(raw, 'width', 'gphoto')),
        'height': int(gvalue(raw, 'height', 'gphoto')),
        'summary': gvalue(raw, 'summary'),
        'album_id': gvalue(raw, 'albumid', 'gphoto'),
    }
    return GooglePhoto(**res)


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

    def _url(self, suffix=''):
        return 'https://picasaweb.google.com/data/feed/api/user/%s/%s' % (
            self.login, suffix)

    def _headers(self):
        return {
            'GData-Version': '2',
            'Content-Type': 'application/atom+xml',
            'Authorization': 'GoogleLogin auth=%s' % self.token
        }

    def _params(self, page_size, index=1):
        return {
            'alt': self.data_type,
            'max-results': page_size,
            'start-index': index,
        }

    def _paginated_fetch(self, url, params, callback, page_size=None, index=1):
        """Returns an iterator to a paginated resource.
        """
        if page_size is None:
            page_size = self.page_size
        # update the page number
        scope_params = self._params(page_size, index)
        scope_params.update(params)
        # get the page
        log.debug("url = '%s', params = '%s'" % (url, json.dumps(scope_params)))
        res = requests.get(url, params=scope_params, headers=self._headers())
        if res.status_code != 200:
            raise ValueError("could not fetch Google resource: '%s'" % url)
        data = res.json()['feed']
        for item in data['entry']:
            yield callback(item)
        # keep going until all data is consumed
        total_results = gvalue(data, 'totalResults', 'openSearch')
        remaining_results = total_results - (index + page_size - 1)
        if remaining_results > 0:
            for item in self._paginated_fetch(url, params, callback, page_size, index + page_size):
                yield item

    def fetch_albums(self, page_size=None):
        url = self._url()  # albums are requested via 'kind' param on base URL
        params = {'kind': 'album'}
        return self._paginated_fetch(url, params, raw2album, page_size)

    def fetch_images(self, album_id, page_size=None):
        url = self._url('albumid/%s' % album_id)
        params = {'kind': 'photo'}
        return self._paginated_fetch(url, params, raw2photo, page_size)
