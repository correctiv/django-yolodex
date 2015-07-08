import re
import os
import errno

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import resolve

IS_FILE_RE = re.compile(r'\.([a-z]{2,4})$')
YOLODEX_MEDIA_PATH = u'yolodex/sources/{}/{}'


def get_current_app(request):
    return resolve(request.path).namespace


def get_media_path(realm, path):
    return YOLODEX_MEDIA_PATH.format(realm.pk, path)


def get_absolute_media_path(realm, path):
    return os.path.join(settings.MEDIA_ROOT, get_media_path(realm, path))


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_domain(url):
    o = urlparse(url)
    return o.netloc


def get_sources(realm, sources):
    for kind, source, extra in get_raw_sources(realm, sources):
        if kind == 'file':
            source = get_media_path(realm, source)
        yield kind, source, extra


def get_raw_sources(realm, sources):
    for line in sources.splitlines():
        if not line.strip():
            continue
        match = IS_FILE_RE.search(line)
        if line.startswith(('http://', 'https://')):
            extra = get_domain(line)
            if match is not None:
                extra = u'%s (%s)' % (extra, match.group(1).upper())
            yield ('url', line, extra)
        elif match is not None:
            ext = match.group(1).upper()
            yield ('file', line, ext)
        else:
            yield ('text', line, '')
