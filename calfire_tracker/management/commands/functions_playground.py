from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from calfire_tracker.models import CalWildfire
import csv, time, datetime, logging, re, types
from datetime import tzinfo
import pytz
from pytz import timezone
from dateutil import parser
from titlecase import titlecase
from scraper_configs import BaseScraper

# log everything and send to stderr #
logging.basicConfig(level=logging.DEBUG)

data_dict_to_scan = [
    {'estimated_containment': '406 lightning strikes, for a total of 73 confirmed fires.'},
    {'estimated_containment': '406 acres -50%contained'},
    {'estimated_containment': '406 acres - 100% contained'},
    {'estimated_containment': '406 acres'},

    {'acres_burned_containmentt': '1,406 lightning strikes, for a total of 73 confirmed fires.'},
    {'acres_burned_containment': '1,406 acres -50%contained'},
    {'acres_burned_containment': '1,406 acres - 100% contained'},
    {'acres_burned_containment': '1,406 acres'},

    {'containment': '6 lightning strikes, for a total of 73 confirmed fires.'},
    {'containment': '6 acres -50%contained'},
    {'containment': '6 acres - 100% contained'},
    {'containment': '6 acres'},

    {'status_notes': '10,406 lightning strikes, for a total of 73 confirmed fires.'},
    {'status_notes': '10,406 acres -50%contained'},
    {'status_notes': '10,406 acres - 100% contained'},
    {'status_notes': '10,406 acres'},
]





def loop_through_dict(list_of_dicts):
    for dict in list_of_dicts:
        for key, value in dict.iteritems():
            evaluate_for_percent_sign(key, value)






def evaluate_for_percent_sign(dictionary_key, dictionary_value):
    ''' sees if a percent sign in present in a given string '''
    percent_sign = re.search('%', dictionary_value)
    try:
        if percent_sign:
            message = True
            target_key = dictionary_key
            target_value = dictionary_value
        else:
            message = False
            target_key = dictionary_key
            target_value = None
    except:
        message = False
        target_key = dictionary_key
        target_value = 'exception'

    logging.debug(message)
    return target_value





















def evaluate_for_initial_digit(string_to_match):
    ''' runs regex on string to see it begins with a digit '''
    initial_digit_check = re.compile('^\d+')
    match = re.search(initial_digit_check, string_to_match)
    try:
        if match:
            target_number = string_to_match.replace(',', '')
            target_figure = evaluate_for_acres_and_extract(target_number)
        else:
            target_figure = None
    except:
        target_figure = 'exception'
    logging.debug(target_figure)
    return target_figure

def evaluate_for_acres_and_extract(string_to_match):
    ''' runs regex on string to see it contains acreage figures, and if so extracts figure '''
    word_to_evaluate = 'acres'
    acres_check = re.compile(r'\d+\s\b%s\b' % (word_to_evaluate), re.I)
    extract_number = re.compile('\d+')
    acres_match = re.search(acres_check, string_to_match)
    try:
        if acres_match:
            target_number = re.search(extract_number, string_to_match)
            target_number = target_number.group()
            target_number = int(target_number)
        else:
            target_number = None
    except:
        target_number = 'exception'
    return target_number





















class Command(BaseCommand):
    help = 'Scrapes California Wildfires data'
    def handle(self, *args, **options):
        loop_through_dict(data_dict_to_scan)