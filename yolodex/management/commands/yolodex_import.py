from optparse import make_option

import unicodecsv

from django.core.management.base import BaseCommand

from ...models import Realm
from ...utils import import_graph


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
        realm_slug, nodes_filename, edges_filename = args
        realm = Realm.objects.get(slug=realm_slug)
        nodes = unicodecsv.DictReader(open(nodes_filename))
        edges = unicodecsv.DictReader(open(edges_filename))

        import_graph(realm, nodes, edges, clear=options['clear'])
