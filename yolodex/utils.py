import shutil
import re
import os
import errno

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import resolve
from django.template.defaultfilters import slugify


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


def get_from_cache_or_create(type_slug, klass, cache, realm):
    if type_slug in cache:
        typ = cache[type_slug]
    else:
        typ = klass.objects.filter(realms=realm, translations__slug=slugify(type_slug))
        if typ:
            typ = typ[0]
        else:
            typ = klass()
            typ.set_current_language('en')
            typ.name = type_slug
            typ.slug = slugify(type_slug)
            typ.save()
            typ.realms.add(realm)
        cache[type_slug] = typ
    return typ


def import_graph(realm, nodes, edges, media_dir=None, clear=False):

    from .models import Entity, Relationship

    entity_typ_cache = {}
    entity_cache = {}

    if clear:
        Entity.objects.filter(realm=realm).delete()
        Relationship.objects.filter(realm=realm).delete()

    for node in nodes:
        entity = create_entity(realm, node, entity_cache, entity_typ_cache)
        print "Entity %s created" % entity
        if entity is not None and media_dir is not None:
            raw_sources = get_raw_sources(realm, entity.sources)
            import_sources(realm, [s[1] for s in raw_sources if s[0] == 'file'], media_dir)

    rel_typ_cache = {}
    for edge in edges:
        rel = create_relationship(realm, edge, entity_cache, rel_typ_cache)
        print "Relationship %s created" % rel
        if rel is not None and media_dir is not None:
            raw_sources = get_raw_sources(realm, rel.sources)
            import_sources(realm, [s[1] for s in raw_sources if s[0] == 'file'], media_dir)


def import_sources(realm, sources, media_dir):
    for source in sources:
        src = os.path.join(media_dir, source).encode('utf-8')
        target = get_absolute_media_path(realm, source).encode('utf-8')
        target_dir = os.path.dirname(target)
        mkdir_p(target_dir)
        if not os.path.exists(target):
            shutil.copyfile(src, target)


def create_entity(realm, node, entity_cache, entity_typ_cache):
    from .models import Entity, EntityType

    name = node.pop('label')
    slug = node.pop('id', slugify(name))
    if not slug:
        return
    type_slug = node.pop('type', None)
    typ = None
    if type_slug is not None:
        typ = get_from_cache_or_create(type_slug, EntityType, entity_typ_cache, realm)

    sources = node.pop('sources', '')
    data = {k: v for k, v in node.items() if v}
    try:
        entity = Entity.objects.get(slug=slug, realm=realm)
    except Entity.DoesNotExist:
        entity = Entity.objects.create(
            name=name,
            slug=slug,
            realm=realm,
            sources=sources,
            type=typ,
            data=data
        )
    entity_cache[slug] = entity
    return entity


def create_relationship(realm, edge, entity_cache, rel_typ_cache):
    from .models import Relationship, RelationshipType

    source_slug = edge.pop('source')
    if not source_slug:
        return
    source = entity_cache[source_slug]
    target_slug = edge.pop('target')
    if not target_slug:
        return
    target = entity_cache[target_slug]
    sources = edge.pop('sources', '')
    reltype_slug = edge.pop('relationtype', None)
    reltype = None
    if reltype_slug:
        reltype = get_from_cache_or_create(reltype_slug, RelationshipType, rel_typ_cache, realm)
    edge_type = edge.pop('type', 'directed')
    data = {k: v for k, v in edge.items() if v}
    rel, created = Relationship.objects.get_or_create(
        realm=realm,
        source=source,
        target=target,
        type=reltype,
        defaults=dict(
            sources=sources,
            directed=edge_type == 'directed',
            data=data
        )
    )
    return rel
