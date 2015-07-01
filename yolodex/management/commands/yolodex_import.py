from optparse import make_option

import unicodecsv

from django.core.management.base import BaseCommand

from ...models import Realm
from ...utils import import_graph, assign_degree


class Command(BaseCommand):
    args = '<realm> <nodes file> <edges file>'
    help = 'Imports graphs and edges into realm'

    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clear all entities/relationships in the given realm before import'),
    )

    def handle(self, *args, **options):
        realm_slug, nodes_filename, edges_filename = args[:3]
        media_dir = None
        if len(args) > 3:
            media_dir = args[3]
        realm = Realm.objects.get(slug=realm_slug)
        nodes = unicodecsv.DictReader(open(nodes_filename))
        edges = unicodecsv.DictReader(open(edges_filename))
        self.stdout.write('Importing graph to %s' % realm)
        import_graph(realm, nodes, edges, media_dir=media_dir, clear=options['clear'])
        self.stdout.write('Assigning degrees of %s' % realm)
        assign_degree(realm)
