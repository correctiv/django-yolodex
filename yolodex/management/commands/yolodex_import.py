import unicodecsv

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from ...models import Realm, Entity, EntityType, Relationship, RelationshipType


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


class Command(BaseCommand):
    args = '<realm> <nodes file> <edges file>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        entity_typ_cache = {}
        entity_cache = {}
        realm_slug, nodes_filename, edges_filename = args
        realm = Realm.objects.get(slug=realm_slug)
        nodes = unicodecsv.DictReader(open(nodes_filename))
        edges = unicodecsv.DictReader(open(edges_filename))

        Entity.objects.filter(realm=realm).delete()
        Relationship.objects.filter(realm=realm).delete()

        for node in nodes:
            name = node.pop('label')
            slug = node.pop('id', slugify(name))
            if not slug:
                continue
            type_slug = node.pop('type', None)
            typ = None
            if type_slug is not None:
                typ = get_from_cache_or_create(type_slug, EntityType, entity_typ_cache, realm)

            data = {k: v for k, v in node.items() if v}
            try:
                entity = Entity.objects.get(slug=slug, realm=realm)
            except Entity.DoesNotExist:
                entity = Entity.objects.create(
                    name=name,
                    slug=slug,
                    realm=realm,
                    type=typ,
                    data=data
                )
            print "Entity %s created" % entity
            entity_cache[slug] = entity

        rel_typ_cache = {}
        for edge in edges:
            source_slug = edge.pop('source')
            if not source_slug:
                continue
            source = entity_cache[source_slug]
            target_slug = edge.pop('target')
            if not target_slug:
                continue
            target = entity_cache[target_slug]
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
                directed=edge_type == 'directed',
                data=data
            )
            print "Relationship %s created" % rel
