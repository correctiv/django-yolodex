import json
import random


class Network(object):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            'nodes': [self.node_to_dict(n) for n in self.nodes],
            'edges': [self.edge_to_dict(e) for e in self.edges],
        }

    def node_to_dict(self, node):
        return {
            'id': str(node.id),
            'name': node.name,
            'url': node.get_absolute_url(),
            'type': node.type.slug,
            'data': node.data
        }

    def edge_to_dict(self, edge):
        return {
            'id': str(edge.id),
            'source': str(edge.source_id),
            'target': str(edge.target_id),
            'data': edge.data
        }
