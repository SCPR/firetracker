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

''' old functions I am building off of '''

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
    help = 'looping through dict for numbers'
    def handle(self, *args, **options):
        loop_through_dict(data_dict_to_scan)


''' learning how the date come back with time zone info '''

date_time_parse = 'July 18, 2013 9:45 am'

def convert_time_to_nicey_format(date_time_parse):
    ''' work crazy datetime magic that might be working '''
    ''' based on http://stackoverflow.com/questions/17193228/python-twitter-api-tweet-timestamp-convert-from-utc-to-est '''
    utc = timezone('UTC')
    pacific = pytz.timezone('US/Pacific')

    # check the date being pulled
    logging.debug(date_time_parse)

    # parse the date to datetime.datetime
    date_time_parse = parser.parse(date_time_parse)
    logging.debug(date_time_parse)

    # register it as pacific time zone
    pacificizd_date_time_parse = pacific.localize(date_time_parse)
    logging.debug(pacificizd_date_time_parse)
    logging.debug('%s - %s' % (pacificizd_date_time_parse.strftime("%A, %d, %B %Y %I:%M%p"), pacificizd_date_time_parse.tzinfo))

    #logging.debug(date_time_parse.tzinfo)
    #logging.debug('%s %s' % (utc_izd_datetime.strftime("%A, %d. %B %Y %I:%M%p"), utc_izd_datetime.tzinfo))
    #logging.debug('%s %s' % (pacific_izd_datetime.strftime("%A, %d. %B %Y %I:%M%p"), pacific_izd_datetime.tzinfo))

    #date_time_object = datetime.datetime(2013, 7, 18, 9, 45)
    #logging.debug(date_time_object.strftime("%A, %d. %B %Y %I:%M%p"))

    #target_datetime = utc.localize(parser.parse(date_to_parse))
    #target_datetime = utc_datetime.astimezone(pacific)

    #los_angeles = pytz.timezone('US/Pacific')
    #target_datetime = los_angeles.localize(parser.parse(date_to_parse))

    return pacificizd_date_time_parse

'''
class Command(BaseCommand):
    help = 'tests dates'
    def handle(self, *args, **options):
        convert_time_to_nicey_format(date_time_parse)
'''