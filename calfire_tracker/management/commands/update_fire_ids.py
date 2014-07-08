from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.core.mail import send_mail, mail_admins, send_mass_mail, EmailMessage
from django.conf import settings
from calfire_tracker.models import CalWildfire
import csv
import time
import datetime
import logging
import re
import types
import pytz
import requests
from datetime import tzinfo
from pytz import timezone
from dateutil import parser
from titlecase import titlecase
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
)


class Command(BaseCommand):
    help = 'Looks at records in the database'
    def handle(self, *args, **options):
        update_fire_id_in_db()


def update_fire_id_in_db():
    wildfires = CalWildfire.objects.all()
    for fire in wildfires:
        if fire.year < 2014:
            updated_fire_id = "%s-%s" % (fire.created_fire_id, fire.year)
            fire.created_fire_id = updated_fire_id
            fire.save()