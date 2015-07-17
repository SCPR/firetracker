from django.conf import settings
from django.core.management.base import BaseCommand
import datetime
import logging
from calfire_tracker.data_manager import WildfireDataClient

logger = logging.getLogger("calfire_tracker")

class Command(BaseCommand):
    help = "Scrapes California Wildfires data from CalFire and some Inciweb Pages"
    def handle(self, *args, **options):
        task_run = WildfireDataClient()
        task_run._init()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
