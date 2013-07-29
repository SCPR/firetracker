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
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup
from scraper_configs import BaseScraper

logging.basicConfig(level=logging.DEBUG)

class fire_instance():
    def __init__(self, name, county):
        self.name = name
        self.county = county

def retrieve_data_from_page():
    ''' save raw html from a web page locally '''
    raw_content = BaseScraper()
    target_data = raw_content.create_instance_of_mechanize('http://cdfdata.fire.ca.gov/incidents/incidents_current?pc=500')

def open_file_and_parse_for_soup(local_file):
    ''' open local file and parse for soup '''
    target_data = BeautifulSoup(open(local_file), convertEntities=BeautifulSoup.HTML_ENTITIES)
    target_data = target_data.findAll('table', {'class': 'incident_table'})[1:]
    isolate(target_data)

def save_fire_details_to_dict(data_rows):
    ''' go through each table and write the data to a dictionary '''
    data_dict = {}
    for row in data_rows:
        target_cell = row.findAll('td')
        details_information = determine_if_details_link_present(target_cell)
        if details_information is not None:
            for key, value in details_information.iteritems():
                data_dict[key] = value
        else:
            pass
        target_key = lowercase_remove_colon_and_replace_space_with_underscore(target_cell[0].text.encode('utf-8'))
        target_data = target_cell[1].text.encode('utf-8')
        data_dict[target_key] = target_data
    return data_dict

def determine_if_details_link_present(target_cell):
    ''' extracts an anchor tag if present in cell, determine source and create dictionary '''
    target_text = target_cell[1].findAll('a')
    if len(target_text) == 0:
        pass
    else:
        data_dict = {}
        for link in target_text:
            try:
                target_class = link['class']
            except KeyError:
                target_class = ""
            if (target_class == 'bluelink'):
                details_source = 'CalFire'
                details_link = 'http://cdfdata.fire.ca.gov' + link['href']
            else:
                details_source = 'Other/Inciweb'
                details_link = link['href']
        data_dict['details_source'] = details_source
        data_dict['details_link'] = details_link
        return data_dict

def isolate(table_instance):
    ''' isolate the individual tables '''
    list_of_fires = []
    for table in table_instance:
        data_rows = table.findAll('tr')[1:]
        list_of_fires.append(save_fire_details_to_dict(data_rows))
    check_and_compare_last_update(list_of_fires)










### begin helper and formatting functions ###
def lowercase_remove_colon_and_replace_space_with_underscore(string):
    ''' lowercase_remove_colon_and_replace_space_with_underscore '''
    formatted_data = string.lower().replace(':', '').replace(' ', '_').replace('_-_', '_').replace('/', '_')
    return formatted_data

def slugifyFireName(string):
    ''' lowercase_and_replace_space_with_dash '''
    formatted_data = string.lower().replace(':', '-').replace(' ', '-').replace('_', '-').replace('_-_', '-').replace('/', '-')
    return formatted_data

def hashtagifyFireName(string):
    ''' lowercase_and_replace_space_with_dash '''
    formatted_data = titlecase(string).replace(' ', '')
    return formatted_data

def convert_time_to_nicey_format(date_time_parse):
    ''' work crazy datetime magic that might be working '''
    ''' based on http://stackoverflow.com/questions/17193228/python-twitter-api-tweet-timestamp-convert-from-utc-to-est '''
    utc = timezone('UTC')
    pacific = pytz.timezone('US/Pacific')
    date_time_parse = parser.parse(date_time_parse)
    pacificizd_date_time_parse = pacific.localize(date_time_parse)
    return pacificizd_date_time_parse

def extract_link_from_cells(row_name):
    ''' extract more_info link from cell '''
    target_cell = row_name.findAll('td')
    try:
        target_link = 'http://cdfdata.fire.ca.gov' + target_cell[0].a['href']
    except:
        target_link = None
    return target_link

def extract_initial_integer(string_to_match):
    ''' runs regex on acres cell to return acres burned as int '''
    number_check = re.compile('^\d+')
    extract_number = re.compile('\d+')
    match = re.search(number_check, string_to_match)
    try:
        if match:
            target_number = string_to_match.replace(',', '')
            logging.debug(target_number)
            target_number = re.search(extract_number, target_number)
            target_number = target_number.group()
            target_number = int(target_number)
            logging.debug(target_number)

        else:
            target_number = None
            logging.debug(target_number)
    except:
        target_number = 'exception'
        logging.debug(target_number)

    return target_number

def extract_containment_amount(string_to_match):
    ''' runs regex on acres cell to return containment as int '''
    extract_number = re.compile('\d+')
    determine_hyphen = re.compile('-')
    percent_match = re.search('%', string_to_match)
    try:
        if percent_match:
            hyphen_match = re.search(determine_hyphen, string_to_match)
            if hyphen_match:
                target_number = re.split('-', string_to_match)
                logging.debug(target_number)
                target_number = re.search(extract_number, target_number[1])
                target_number = target_number.group()
                target_number = int(target_number)
                logging.debug(target_number)
            else:
                target_number = 100
        else:
            target_number = None
    except:
        target_number = 'exception'
    return target_number

class Command(BaseCommand):
    help = 'Scrapes California Wildfires data'
    def handle(self, *args, **options):
        self.stdout.write('\nScraping started at %s\n' % str(datetime.datetime.now()))
        open_file_and_parse_for_soup('incidents_current.html')
        self.stdout.write('\nScraping finished at %s\n' % str(datetime.datetime.now()))