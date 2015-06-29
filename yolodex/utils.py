from django.core.urlresolvers import resolve
from django.template.defaultfilters import slugify

from .models import Entity, EntityType, Relationship, RelationshipType


def get_current_app(request):
    return resolve(request.path).namespace


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


def import_graph(realm, nodes, edges, clear=False):
    entity_typ_cache = {}
    entity_cache = {}

    if clear:
        Entity.objects.filter(realm=realm).delete()
        Relationship.objects.filter(realm=realm).delete()

    for node in nodes:
        entity = create_entity(realm, node, entity_cache, entity_typ_cache)
        print "Entity %s created" % entity

    rel_typ_cache = {}
    for edge in edges:
        rel = create_relationship(realm, edge, entity_cache, rel_typ_cache)
        print "Relationship %s created" % rel


def create_entity(realm, node, entity_cache, entity_typ_cache):
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
    rel = Relationship.objects.create(
        realm=realm,
        source=source,
        target=target,
        type=reltype,
        sources=sources,
        directed=edge_type == 'directed',
        data=data
    )
    return rel
