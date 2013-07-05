from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc
from wildfires.models import Wildfire
import csv
import pytz
import time, datetime
import logging
import re
import types
from dateutil import parser
from titlecase import titlecase
from scraper_configs import BaseScraper

# log everything and send to stderr
logging.basicConfig(level=logging.DEBUG)

csv_field_names = [
    'name',
    'county',
    'location',
    'administrative_unit',
    'acres',
    'containment',
    'notes',
    'date_started',
    'last_update',
    'more_info',
]

paging_itertator = [0, 1, 2, 3, 4, 5, 6, 7, 8]

def write_data_header(csvfile_name):
    ''' writes csv header rows from a given table '''
    logging.debug('running extract_data_header function')
    csvfile_name.writerow(csv_field_names)

def construct_url_to_scrape():
    ''' constructs URL to scrape, opens news csv file, write rows to csv file  '''
    logging.debug('running construct_url_to_scrape function')

    filename_complete = 'wildfires.csv'
    with open(filename_complete, 'wb', buffering=0) as newCsvFile:
        csvfile_name = csv.writer(newCsvFile, delimiter=',', quoting=csv.QUOTE_ALL)
        write_data_header(csvfile_name)
        for url in paging_itertator:
            url_target = 'http://cdfdata.fire.ca.gov/incidents/incidents_current?sort=incident_priority%20&pc=5&cp=' + str(url)
            extract_data_table(url_target, csvfile_name)
    newCsvFile.close()

def extract_data_table(url_target, csvfile_name):
    ''' extracts a given table for scraping '''
    logging.debug('running extract_data function')
    content_scrape = BaseScraper()
    data_table = content_scrape.create_instance_of_mechanize(url_target)
    data_table = data_table.findAll('table', {'class': 'incident_table'})[1:]
    extract_data_from_rows(data_table, csvfile_name)

def extract_data_from_rows(data_table, csvfile_name):
    logging.debug('extract_data_from_rows')
    for table in data_table:
        data_rows = table.findAll('tr')
        fire_name = extract_data_from_cells(data_rows[1])
        county = extract_data_from_cells(data_rows[2])
        fire_location = extract_data_from_cells(data_rows[3])
        administrative_unit = extract_data_from_cells(data_rows[4])
        notes = extract_data_from_cells(data_rows[5])
        acres_burned = extract_acreage_amount(notes)
        containment_percent = extract_containment_amount(notes)
        date_started = parser.parse(extract_data_from_cells(data_rows[6]))
        last_update = parser.parse(extract_data_from_cells(data_rows[7]))
        more_info = extract_link_from_cells(data_rows[0])

        # build a list of data
        data_scraped_for_csv = [
            fire_name,
            county,
            fire_location,
            administrative_unit,
            acres_burned,
            containment_percent,
            notes,
            date_started,
            last_update,
            more_info,
        ]

        #csvfile_name.writerow(data_scraped_for_csv)

        try:
            obj = Wildfire.objects.get(fire_name=fire_name)
            obj.fire_name = fire_name
            obj.county = county
            obj.location = fire_location,
            obj.administrative_unit = administrative_unit,
            obj.acres_burned = acres_burned,
            obj.containment_percent = containment_percent,
            obj.notes = notes,
            obj.date_time_started = date_started,
            obj.last_updated = last_update,
            obj.more_info = more_info,
            obj.save()
        except Wildfire.DoesNotExist:
            obj = Wildfire(fire_name = fire_name, county = county, location = fire_location, administrative_unit = administrative_unit, acres_burned = acres_burned, containment_percent = containment_percent, notes = notes, date_time_started = date_started, last_updated = last_update, more_info = more_info)
            obj.save()

def extract_data_from_cells(row_name):
    ''' extract data from normal cell '''
    target_cell = row_name.findAll('td')
    target_data = target_cell[1].text.encode('utf-8')
    return target_data

def extract_link_from_cells(row_name):
    ''' pulls link for more detail from cell '''
    target_cell = row_name.findAll('td')
    try:
        target_data = 'http://cdfdata.fire.ca.gov' + target_cell[0].a['href']
    except:
        target_data = None
    return target_data

def extract_acreage_amount(string_to_match):
    ''' pulls acreage amount from cell '''
    number_check = re.compile('\d+')
    extract_number = re.compile('\d+\s')
    match = re.search(number_check, string_to_match)

    try:
        if match:
            target_number = string_to_match.replace(',', '')
            target_number = re.search(extract_number, target_number)
            target_number = int(target_number.group())
        else:
            target_number = None

    except:
        target_number = 'exception'

    return target_number

def extract_containment_amount(string_to_match):
    ''' pulls containment amount from cell '''
    extract_number = re.compile('\d+')
    determine_hyphen = re.compile('-')
    percent_match = re.search('%', string_to_match)

    try:
        if percent_match:
            hyphen_match = re.search(determine_hyphen, string_to_match)
            if hyphen_match:
                target_number = re.split('-', string_to_match)
                target_number = re.search(extract_number, target_number[1])
                target_number = int(target_number.group())
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
        self.stdout.write('\nScraping finished at %s\n' % str(datetime.datetime.now()))
        construct_url_to_scrape()