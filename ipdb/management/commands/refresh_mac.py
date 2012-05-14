from django.core.management.base import BaseCommand, CommandError

from switch.models import *

class Command(BaseCommand):
    args = '<none>'
    help = 'Refresh data from switches'
    def handle(self, *args, **options):
        switches = Switch.objects.all()
        for switch in switches:
            switch.refresh_mac()

