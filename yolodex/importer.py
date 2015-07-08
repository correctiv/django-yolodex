import shutil
import logging
import os
import io

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

from django.template.defaultfilters import slugify

import networkx as nx
import unicodecsv

from .models import Entity, EntityType, Relationship, RelationshipType
from .utils import get_raw_sources, get_absolute_media_path, mkdir_p

logger = logging.getLogger(__name__)


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


def update_object(obj, dic):
    changed = False
    for k, v in dic.items():
        if getattr(obj, k) != v:
            setattr(obj, k, v)
            changed = True
    return changed

STAT_VALUES = {
    None: 'unchanged',
    False: 'updated',
    True: 'created'
}


def update_or_create(klass, search_dict, attr_dict):
    created = True
    try:
        obj = klass.objects.get(**search_dict)
        created = None
        if update_object(obj, attr_dict):
            created = False
            obj.save()
    except klass.DoesNotExist:
        attr_dict.update(search_dict)
        obj = klass.objects.create(**attr_dict)
    return obj, created


class YolodexImporter(object):
    entity_type_cache = {}
    rel_typ_cache = {}
    entity_cache = {}

    def __init__(self, realm):
        self.realm = realm
        self.stats = {
            'entity_created': 0,
            'entity_updated': 0,
            'entity_deleted': 0,
            'entity_unchanged': 0,
            'relationship_created': 0,
            'relationship_updated': 0,
            'relationship_deleted': 0,
            'relationship_unchanged': 0,
        }

    def import_graph_from_urls(self, node_url, edge_url, consume=True, **kwargs):
        node_file = urlopen(node_url)
        edge_file = urlopen(edge_url)
        if consume:
            node_file = io.BytesIO(node_file.read())
            edge_file = io.BytesIO(edge_file.read())
        self.import_graph_from_files(node_file, edge_file, **kwargs)

    def import_graph_from_files(self, node_file, edge_file, **kwargs):
        nodes = unicodecsv.DictReader(node_file)
        edges = unicodecsv.DictReader(edge_file)
        self.import_graph(nodes, edges)

    def import_graph(self, nodes, edges, media_dir=None, clear=False, update=False):
        if clear:
            self.clear()

        self.version = self.realm.version
        self.old_version = None
        if update:
            self.old_version = self.version
            self.version = self.version + 1

        self.create_nodes(nodes, media_dir=media_dir)
        self.create_relationships(edges, media_dir=media_dir)

        if update:
            self.realm = self.version
            self.realm.save()
            self.clear_old_versions()

    def assign_degree(self):
        mg = nx.MultiDiGraph()
        mg.add_nodes_from(Entity.objects.filter(realm=self.realm))
        mg.add_edges_from((r.source, r.target) for r in Relationship.objects.filter(realm=self.realm))
        for entity, deg in mg.in_degree_iter():
            entity.in_degree = deg
        for entity, deg in mg.out_degree_iter():
            entity.out_degree = deg
        for entity, deg in mg.degree_iter():
            entity.degree = deg
        for entity in mg.nodes_iter():
            entity.save()

    def create_nodes(self, nodes, media_dir=None):
        for node in nodes:
            entity = self.create_entity(node)
            if entity is not None and media_dir is not None:
                raw_sources = get_raw_sources(self.realm, entity.sources)
                self.import_sources([s[1] for s in raw_sources if s[0] == 'file'], media_dir)

    def create_relationships(self, edges, media_dir=None):
        for edge in edges:
            rel = self.create_relationship(edge)
            if rel is not None and media_dir is not None:
                raw_sources = get_raw_sources(self.realm, rel.sources)
                self.import_sources([s[1] for s in raw_sources if s[0] == 'file'], media_dir)

    def import_sources(self, sources, media_dir):
        for source in sources:
            src = os.path.join(media_dir, source).encode('utf-8')
            target = get_absolute_media_path(self.realm, source).encode('utf-8')
            target_dir = os.path.dirname(target)
            mkdir_p(target_dir)
            if not os.path.exists(target):
                shutil.copyfile(src, target)

    def clear(self):
        logger.info("Deleting all entities/relationships of realm %s", self.realm)
        self.delete_entities(Entity.objects.filter(realm=self.realm))
        self.delete_relationships(Relationship.objects.filter(realm=self.realm).delete())

    def clear_old_versions(self):
        logger.info("Deleting entities/relationships of realm %s with old version %s", self.realm, self.old_version)
        e_qs = Entity.objects.filter(realm=self.realm, version=self.old_version)
        self.delete_entities(e_qs)

        r_qs = Relationship.objects.filter(realm=self.realm, version=self.old_version)
        self.delete_relationships(r_qs)

    def create_entity(self, node):
        name = node.pop('name')
        slug = node.pop('id', slugify(name))
        if not slug:
            return
        type_slug = node.pop('type', None)
        typ = None
        if type_slug is not None:
            typ = self.get_entitytype(type_slug)

        sources = node.pop('sources', '')
        data = {k: v for k, v in node.items() if v}

        search_dict = {
            'slug': slug,
            'realm': self.realm
        }
        attr_dict = dict(
            name=name,
            sources=sources,
            type=typ,
            data=data,
            version=self.version
        )
        entity, created = update_or_create(Entity, search_dict, attr_dict)
        logger.info("Entity %s %s", entity, STAT_VALUES[created])
        self.record_entity_stat(created)
        self.entity_cache[slug] = entity
        return entity

    def create_relationship(self, edge):
        source_slug = edge.pop('source')
        if not source_slug:
            return
        source = self.entity_cache[source_slug]
        target_slug = edge.pop('target')
        if not target_slug:
            return
        target = self.entity_cache[target_slug]
        sources = edge.pop('sources', '')
        reltype_slug = edge.pop('relationtype', None)
        reltype = None
        if reltype_slug:
            reltype = self.get_relationshiptype(reltype_slug)
        edge_type = edge.pop('type', 'directed')
        data = {k: v for k, v in edge.items() if v}

        search_dict = dict(
            realm=self.realm,
            source=source,
            target=target,
            type=reltype,
            data=data,
        )
        attr_dict = dict(
            directed=edge_type == 'directed',
            sources=sources,
            version=self.version
        )
        rel, created = update_or_create(Relationship, search_dict, attr_dict)
        logger.info("Relationship %s %s", rel, STAT_VALUES[created])
        self.record_relationship_stat(created)
        return rel

    def delete_entities(self, e_qs):
        self.stats['entity_deleted'] = e_qs.count()
        e_qs.delete()

    def delete_relationships(self, r_qs):
        self.stats['relationsip_deleted'] = r_qs.count()
        r_qs.delete()

    def get_entitytype(self, type_slug):
        return get_from_cache_or_create(type_slug, EntityType, self.entity_type_cache, self.realm)

    def get_relationshiptype(self, reltype_slug):
        return get_from_cache_or_create(reltype_slug, RelationshipType, self.rel_typ_cache, self.realm)

    def record_stat(self, typ, created):
        self.stats['%s_%s' % (typ, STAT_VALUES[created])] += 1

    def record_entity_stat(self, created):
        self.record_stat('entity', created)

    def record_relationship_stat(self, created):
        self.record_stat('relationship', created)
