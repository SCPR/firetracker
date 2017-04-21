from django.conf import settings
from django.core.management.base import BaseCommand
import datetime
import logging
from calfire_tracker.manager_calfire import RetrieveCalFireCurrentIncidents

logger = logging.getLogger("calfire_tracker")

class Command(BaseCommand):

    help = "Scrapes California Wildfires data from CalFire and some Inciweb Pages"

    def calfire_current_incidents(self, *args, **options):
        task_run = RetrieveCalFireCurrentIncidents()
        task_run._init()
        self.stdout.write("Finished retrieving CalFire current incidents at %s\n" % str(datetime.datetime.now()))


    def handle(self, *args, **options):
        self.calfire_current_incidents()
        self.stdout.write("Finished this data import at %s\n" % str(datetime.datetime.now()))

