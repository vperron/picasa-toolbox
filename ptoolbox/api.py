# -*- coding: utf-8 -*-

"""Implements methods to interact with the Picasa Wweb Albums API 2.0,
cf. https://developers.google.com/picasa-web/docs/2.0/reference
"""

import re
import json
import requests

from datetime import datetime, timedelta
from xml.etree import ElementTree

from ptoolbox import log

from .conf import settings
from .utils import iso8601str2datetime
from .models import GoogleAlbum, GooglePhoto, ACCESS_PRIVATE


epoch = datetime.utcfromtimestamp(0)


def ts2dt(ts, millisecs=False):
    """Convert a timestamp to a datetime."""
    if millisecs:
        dt = datetime.utcfromtimestamp(ts / 1000)
        return dt + timedelta(milliseconds=ts % 1000)
    return datetime.utcfromtimestamp(ts)


def dt2ts(dt, millisecs=False):
    """Convert a datetime to a timestamp in UTC."""
    ts = (dt - epoch).total_seconds()
    if millisecs:
        return int(ts * 1000)
    return int(ts)


def g_key(key, namespace=None):
    return key if namespace is None else '%s$%s' % (namespace, key)


def g_value(value, accessor='$t'):
    return {accessor: value}


def g_get_value(data, key, namespace=None, accessor='$t'):
    """Returns a google-encoded value from the feed. Example:
    json = {"gphoto$access": { "$t": "private" }}, then
    g_get_value(json, 'access', 'gphoto') is 'private'
    """
    complete_key = g_key(key, namespace)
    if complete_key in data:
        if accessor in data[complete_key]:
            return data[complete_key][accessor]
    return None


def raw2album(raw):
    """Returns a GoogleAlbum object from the raw JSON data.
    """
    res = {
        'id': g_get_value(raw, 'id', 'gphoto'),
        'title': g_get_value(raw, 'name', 'gphoto'),
        'author': g_get_value(raw['author'][0], 'name'),
        'access': g_get_value(raw, 'access', 'gphoto'),
        'summary': g_get_value(raw, 'summary'),
        'updated': iso8601str2datetime(g_get_value(raw, 'updated')),
        'published': iso8601str2datetime(g_get_value(raw, 'published')),
    }
    return GoogleAlbum(**res)


def raw2photo(raw):
    """Returns a GoogleAlbum object from the raw JSON data.
    """
    res = {
        'id': g_get_value(raw, 'id', 'gphoto'),
        'time': ts2dt(int(g_get_value(raw, 'timestamp', 'gphoto')), millisecs=True),
        'title': g_get_value(raw, 'title'),
        'width': int(g_get_value(raw, 'width', 'gphoto')),
        'height': int(g_get_value(raw, 'height', 'gphoto')),
        'summary': g_get_value(raw, 'summary'),
        'album_id': g_get_value(raw, 'albumid', 'gphoto'),
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
        total_results = g_get_value(data, 'totalResults', 'openSearch')
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

    def create_album(self, title, access=ACCESS_PRIVATE, summary='', location=''):
        ts = dt2ts(datetime.utcnow(), True)
        url = self._url()
        # reverse engineered XML from gdata APIs
        data = '''
        <?xml version="1.0"?>
        <ns0:entry xmlns:ns0="http://www.w3.org/2005/Atom" xmlns:ns1="http://search.yahoo.com/mrss/" xmlns:ns2="http://www.georss.org/georss" xmlns:ns3="http://www.opengis.net/gml" xmlns:ns4="http://schemas.google.com/photos/2007">
        <ns0:category scheme="http://schemas.google.com/g/2005#kind" term="http://schemas.google.com/photos/2007#album"/>
        <ns1:group/>
        <ns0:title type="text">{title}</ns0:title>
        <ns0:summary type="text">{summary}</ns0:summary>
        <ns2:where>
            <ns3:Point>
            <ns3:pos/>
            </ns3:Point>
        </ns2:where>
        <ns4:timestamp>{ts}</ns4:timestamp>
        <ns4:commentingEnabled>true</ns4:commentingEnabled>
        <ns4:access>{access}</ns4:access>
        </ns0:entry>
        '''.format(ts=str(ts), title=title, access=access, summary=summary, location=location).strip()
        res = requests.post(url, data=data, headers=self._headers())
        if res.status_code != 201:
            raise ValueError("could not post new album: '%s'" % title)

        # retrieve newly created album ID
        xml_tree = ElementTree.fromstring(res.text)
        id_node = xml_tree.find('{http://schemas.google.com/photos/2007}id')  # gphoto namespace

        # get album in JSON now
        url = self._url('albumid/%s' % id_node.text)
        params = {'alt': self.data_type}
        res = requests.get(url, params=params, headers=self._headers())
        if res.status_code != 200:
            raise ValueError("could not fetch newly created album: '%s'" % title)
        return raw2album(res.json()['feed'])
