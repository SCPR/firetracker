from django.core.management.base import BaseCommand
from calfire_tracker.tweet_manager import TwitterHashtagSearch
import datetime


class Command(BaseCommand):
    help = "Pulls tweets via and associates with a given fire"

    def handle(self, *args, **options):
        task_run = TwitterHashtagSearch()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
