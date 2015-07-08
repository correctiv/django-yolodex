from optparse import make_option
import logging

from django.core.management.base import BaseCommand

from ...models import Realm
from ...importer import YolodexImporter


class Command(BaseCommand):
    args = '<realm> <nodes file> <edges file>'
    help = 'Imports graphs and edges into realm'

    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clear all entities/relationships in the given realm before import'),
        make_option('--update',
            action='store_true',
            dest='update',
            default=False,
            help='Update realm and entities/relationships to next version'),
    )

    def handle(self, *args, **options):
        realm_slug, nodes_filename, edges_filename = args[:3]
        media_dir = None
        if len(args) > 3:
            media_dir = args[3]
        realm = Realm.objects.get(slug=realm_slug)
        logging.basicConfig(level=logging.INFO)
        self.stdout.write('Importing graph to %s' % realm)
        yimp = YolodexImporter(realm)
        yimp.import_graph_from_files(open(nodes_filename), open(edges_filename),
            media_dir=media_dir,
            clear=options['clear'],
            update=options['update'],
        )
        self.stdout.write('Assigning degrees of %s' % realm)
        yimp.assign_degree()
