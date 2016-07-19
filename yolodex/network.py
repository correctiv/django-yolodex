import json
import functools
import operator

from django.db.models import Q


def undirected_comp(func, r):
    return func(r.source, r.target) or func(r.target, r.source)


def make_network(initial_qs, level=2, include_self=True,
                 rel_filter_op='or_', entity_filter=None):
    """
    FIXME: make this more efficient/less horrible.
    """
    from .models import Relationship

    assert level < 4
    entities = set()
    distance = 0
    if include_self:
        entities |= set([e for e in initial_qs])
    for e in entities:
        e.distance = distance

    relations = set()
    current_level = level
    entity_lookups = [e.pk for e in entities]
    new_entities = set(entity_lookups)
    while current_level > 0:
        distance += 1
        rel_filter_operands = [
            Q(source_id__in=new_entities),
            Q(target_id__in=new_entities)
        ]
        rel_filter_func = lambda x, y: getattr(operator, rel_filter_op)(x, y)
        rel_filter = functools.reduce(rel_filter_func, rel_filter_operands)
        rels = list(Relationship.objects.filter(rel_filter)
                    .distinct('id')
                    .select_related('source', 'target'))
        relations |= set(rels)

        new_entities = set([r.source for r in rels])
        new_entities |= set([r.target for r in rels])
        for e in new_entities:
            e.distance = distance

        if entity_filter is not None:
            new_entities = set([e for e in new_entities if entity_filter(e, rels)])

        entity_lookups = [o.pk for o in new_entities]
        entities |= new_entities
        current_level -= 1
    return Network(entities, relations)


class Network(object):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self, realm=None):
        d = {
            'nodes': [self.node_to_dict(n) for n in self.nodes],
            'edges': [self.edge_to_dict(e) for e in self.edges],
        }
        if realm is not None:
            d['types'] = realm.get_types()
        return d

    def node_to_dict(self, node):
        return {
            'id': str(node.id),
            'name': node.name,
            'url': node.get_absolute_url(),
            'type': node.type.slug,
            'distance': node.distance,
            'degree': node.degree,
            'in_degree': node.in_degree,
            'out_degree': node.out_degree,
            'data': dict(node.data)
        }

    def edge_to_dict(self, edge):
        return {
            'id': str(edge.id),
            'source': str(edge.source_id),
            'target': str(edge.target_id),
            'data': dict(edge.data)
        }
