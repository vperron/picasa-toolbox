# -*- coding: utf-8 -*-

import requests
from xml.etree import ElementTree
from datetime import datetime, timedelta

from .constants import epoch, G_XML_ROOT, G_XML_NAMESPACES, TZ_API_URL


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


def latlon2tz(lat, lon, dt=None):
    if dt is None:
        dt = datetime.now()
    ts = dt2ts(dt)
    url = TZ_API_URL.format(lat=lat, lon=lon, ts=ts)
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception('Could not reach Google Timezone API')
    data = res.json()
    if data[u'status'] != u'OK':
        raise Exception('Could not get a valid answer from Google Timezone API')
    return data


def mail2username(email):
    return email.split('@')[0]  # remove the e-mail part of the login


def iso8601str2datetime(s):
    if s:
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
    return None


def g_json_key(key, namespace=None):
    return key if namespace is None else '%s$%s' % (namespace, key)


def g_json_value(data, key, namespace=None, accessor='$t'):
    """Returns a google-encoded value from the feed. Example:
    json = {"gphoto$access": { "$t": "private" }}, then
    g_json_value(json, 'access', 'gphoto') is 'private'
    """
    complete_key = g_json_key(key, namespace)
    if complete_key in data:
        if accessor in data[complete_key]:
            return data[complete_key][accessor]
    return None


def g_xml_value(data, key, namespace=G_XML_ROOT):
    xml_tree = ElementTree.fromstring(data)
    full_key = "{%s}%s" % (G_XML_NAMESPACES[namespace], key)
    id_node = xml_tree.find(full_key)
    return id_node.text
