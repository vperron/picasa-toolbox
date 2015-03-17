# -*- coding: utf-8 -*-

import os

from datetime import datetime, timedelta

from .path import fastwalk, get_tags, jpeg_size, is_jpeg, md5sum
from .models import ImageInfo
from .google.utils import latlon2tz

TAG_GPS_LAT = 'GPS GPSLatitude'
TAG_GPS_LON = 'GPS GPSLongitude'
TAG_GPS_LAT_REF = 'GPS GPSLatitudeRef'
TAG_GPS_LON_REF = 'GPS GPSLongitudeRef'

TAG_IMAGE_UNIQUE_ID = 'EXIF ImageUniqueID'

TAG_DATETIME_KEYS = (
    'EXIF DateTimeOriginal',
    'EXIF DateTimeDigitized',
    'Image DateTime',  # not used normally. least priority.
)


def gps_convert(s):
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    x = s.replace(u'°',' ').replace('\'',' ').replace('"',' ')
    x = x.split()
    x_dir = x.pop()
    x.extend([0,0,0])
    return (int(x[0])+int(x[1])/60.0+int(x[2])/3600.0) * direction[x_dir]


def count_files(path):
    num_files = 0
    for x in fastwalk(path, deep=True):
        num_files += 1
    return num_files


def tag_str2dt(s):
    return datetime.strptime(str(s), '%Y:%m:%d %H:%M:%S')


def dt2str(dt, separator=' '):
    return dt.strftime('%Y-%m-%d{0}%H%M%S'.format(separator))


def parse_exif_unique_id(tags):
    return tags.get(TAG_IMAGE_UNIQUE_ID, None)


def parse_exif_time(tags):
    values = [tags.get(key, None) for key in TAG_DATETIME_KEYS]
    if not any(values):
        return None
    tag = reduce(lambda a, b: a if a else b, values)  # get first non-null tag
    dt = tag_str2dt(tag)

    # if we have GPS info, let's get the offset.
    gps_lat = tags.get(TAG_GPS_LAT, None)
    gps_lon = tags.get(TAG_GPS_LON, None)
    gps_lat_ref = tags.get(TAG_GPS_LAT_REF, None)
    gps_lon_ref = tags.get(TAG_GPS_LON_REF, None)
    if gps_lat and gps_lon and gps_lat_ref and gps_lon_ref:
        fmt = u'{0}°{1}\'{2}"{3}'
        gps_lat = [eval(str(x)) for x in gps_lat.values]
        gps_lon = [eval(str(x)) for x in gps_lon.values]
        lat_args = gps_lat + [str(gps_lat_ref)[0]]
        lon_args = gps_lon + [str(gps_lon_ref)[0]]
        gps_lat = gps_convert(fmt.format(*lat_args))
        gps_lon = gps_convert(fmt.format(*lon_args))
        zone_data = latlon2tz(gps_lat, gps_lon, dt)
        offset = zone_data[u'rawOffset']
        dt = dt - timedelta(seconds=offset)
    return dt


def list_valid_images(path, deep=True):
    """Walks down a path, yields ImageInfo objects for every 'valid' image.
    A 'valid' image is any file that is JPEG, has minimum info (width, height)
    Time is optional and may be None.
    """
    for e in fastwalk(path, deep):
        if not is_jpeg(e.path):
            continue
        rel_path = os.path.relpath(e.path, path)
        md5 = md5sum(e.path)
        tags = get_tags(e.path)
        time = parse_exif_time(tags)  # this step may take time, may rely on online timezone service
        unique_id = parse_exif_unique_id(tags)
        try:
            width, height = jpeg_size(e.path)
        except ValueError, e:
            continue
        img = ImageInfo(e.path, width, height, md5, time, unique_id, rel_path=rel_path)
        yield img
