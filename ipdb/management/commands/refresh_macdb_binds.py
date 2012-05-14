from django.core.management.base import BaseCommand, CommandError

from switch.models import IPDB

class Command(BaseCommand):
    args = '<none>'
    help = 'Refresh IPDB->MacDB bindings'
    def handle(self, *args, **options):
        ipdbs = IPDB.objects.all()
        for ipdb in ipdbs:
            ipdb.merge_macdb()
