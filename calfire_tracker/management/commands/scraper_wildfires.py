from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from calfire_tracker.models import CalWildfire
import csv, time, datetime, logging, re, types
import pytz
from dateutil import parser
from titlecase import titlecase
from scraper_configs import BaseScraper

# log everything and send to stderr #
logging.basicConfig(level=logging.DEBUG)

# hit url and run functions #
def iterate_through_urls_to_scrape():
    ''' runs a given function based on a list of URLs to scrape '''
    logging.debug('running construct_url_to_scrape function')

    # current url
    url_query = 'http://cdfdata.fire.ca.gov/incidents/incidents_current?pc=500'

    # archive url
    #url_query = 'http://cdfdata.fire.ca.gov/incidents/incidents_archived?archive_year=2012&pc=1&cp=79'

    extract_details_link_if_present(url_query)

# begin first pass, finding links to details pages if present #
def extract_details_link_if_present(url_query):
    ''' extracts a given table for scraping '''
    content_scrape = BaseScraper()
    data_table = content_scrape.create_instance_of_mechanize(url_query)
    data_table = data_table.findAll('table', {'class': 'incident_table'})[1:]
    for table in data_table:
        data_rows = table.findAll('tr')
        target_cell = data_rows[1].findAll('td')
        try:
            fire_name = target_cell[1].text.encode('utf-8')
            details_link = 'http://cdfdata.fire.ca.gov' + target_cell[1].a['href']
        except:
            details_link = None

        # if there isn't a details link, then scrape rows from the index page
        if details_link == None:
            logging.debug('No link so I\'m using the general scraper')
            extract_data_table(table)

        # else scrape rows from details link page
        else:
            logging.debug('Found a link so I\'m using the details scraper')
            extract_details_table(fire_name, details_link)

# begin iterating through non-details items #
def extract_data_table(table):
    ''' extract_data if no details link present '''
    data_rows = table.findAll('tr')[1:]
    data_dict = {}
    for row in data_rows:
        target_cell = row.findAll('td')
        target_key = lowercase_remove_colon_and_replace_space_with_underscore(target_cell[0].text.encode('utf-8'))
        target_data = target_cell[1].text.encode('utf-8')
        data_dict[target_key] = target_data
    save_data_from_dict_to_model(data_dict)

# begin iterating through details items #
def extract_details_table(fire_name, details_link):
    ''' extract target table from details page '''
    details_scrape = BaseScraper()
    details_table = details_scrape.create_instance_of_mechanize(details_link)
    details_table = details_table.findAll('table', {'class': 'incident_table'})
    extract_data_from_cells(fire_name, details_link, details_table)

# extract data amd write to a dict #
def extract_data_from_cells(fire_name, details_link, details_table):
    ''' extract target data from details page '''
    for table in details_table:
        data_rows = table.findAll('tr')[1:]
        data_dict = {}
        data_dict['name'] = fire_name
        data_dict['more_info'] = details_link
        for row in data_rows:
            target_cell = row.findAll('td')
            target_key = lowercase_remove_colon_and_replace_space_with_underscore(target_cell[0].text.encode('utf-8'))
            target_data = target_cell[1].text.encode('utf-8')
            data_dict[target_key] = target_data
        save_data_from_dict_to_model(data_dict)

# function to save data to our database #
def save_data_from_dict_to_model(data_dict):
    ''' save scraped data to data models '''
    logging.debug('processing fire and saving to database')
    logging.debug(data_dict)

    if data_dict.has_key('name'):
        fire_name = data_dict['name']
    else:
        fire_name = 'fire_name'

    if data_dict.has_key('county'):
        county = data_dict['county']
    else:
        county = None

    created_fire_id = '%s-%s' % (fire_name, county)
    twitter_hashtag = '#%s' % (hashtagifyFireName(fire_name))

    if data_dict.has_key('estimated_containment'):
        acres_burned = extract_initial_integer(data_dict['estimated_containment'])
        containment_percent = extract_containment_amount(data_dict['estimated_containment'])
    elif data_dict.has_key('acres_burned_containment'):
        acres_burned = extract_initial_integer(data_dict['acres_burned_containment'])
        containment_percent = extract_containment_amount(data_dict['acres_burned_containment'])
    elif data_dict.has_key('containment'):
        acres_burned = extract_initial_integer(data_dict['containment'])
        containment_percent = extract_containment_amount(data_dict['containment'])
    else:
        acres_burned = None
        containment_percent = None

    if data_dict.has_key('date_time_started'):
        date_time_started = convert_time_to_nicey_format(data_dict['date_time_started'])
    elif data_dict.has_key('date_started'):
        date_time_started = convert_time_to_nicey_format(data_dict['date_started'])
    else:
        date_time_started = None

    if data_dict.has_key('last_updated'):
        last_updated = convert_time_to_nicey_format(data_dict['last_updated'])
    elif data_dict.has_key('last_update'):
        last_updated = convert_time_to_nicey_format(data_dict['last_update'])
    else:
        last_updated = None

    if data_dict.has_key('administrative_unit'):
        administrative_unit = data_dict['administrative_unit']
    else:
        administrative_unit = None

    if data_dict.has_key('more_info'):
        more_info = data_dict['more_info']
    else:
        more_info = None

    fire_slug = '%s' % (slugifyFireName(fire_name))
    county_slug = '%s' % (slugifyFireName(county))

    if data_dict.has_key('location'):
        location = titlecase(data_dict['location'])
    else:
        location = None

    if data_dict.has_key('injuries'):
        injuries = data_dict['injuries']
    else:
        injuries = None

    if data_dict.has_key('evacuations'):
        evacuations = data_dict['evacuations']
    else:
        evacuations = None

    if data_dict.has_key('structures_threatened'):
        structures_threatened = data_dict['structures_threatened']
    else:
        structures_threatened = None

    if data_dict.has_key('structures_destroyed'):
        structures_destroyed = data_dict['structures_destroyed']
    else:
        structures_destroyed = None

    if data_dict.has_key('total_dozers'):
        total_dozers = extract_initial_integer(data_dict['total_dozers'])
    else:
        total_dozers = None

    if data_dict.has_key('total_helicopters'):
        total_helicopters = extract_initial_integer(data_dict['total_helicopters'])
    else:
        total_helicopters = None

    if data_dict.has_key('total_fire_engines'):
        total_fire_engines = extract_initial_integer(data_dict['total_fire_engines'])
    else:
        total_fire_engines = None

    if data_dict.has_key('total_fire_personnel'):
        total_fire_personnel = extract_initial_integer(data_dict['total_fire_personnel'])
    else:
        total_fire_personnel = None

    if data_dict.has_key('total_water_tenders'):
        total_water_tenders = extract_initial_integer(data_dict['total_water_tenders'])
    else:
        total_water_tenders = None

    if data_dict.has_key('total_airtankers'):
        total_airtankers = extract_initial_integer(data_dict['total_airtankers'])
    else:
        total_airtankers = None

    if data_dict.has_key('total_fire_crews'):
        total_fire_crews = extract_initial_integer(data_dict['total_fire_crews'])
    else:
        total_fire_crews = None

    if data_dict.has_key('cause'):
        cause = data_dict['cause']
    else:
        cause = None

    if data_dict.has_key('cooperating_agencies'):
        cooperating_agencies = data_dict['cooperating_agencies']
    else:
        cooperating_agencies = None

    if data_dict.has_key('road_closures_'):
        road_closures = data_dict['road_closures_']
    else:
        road_closures = None

    if data_dict.has_key('conditions'):
        conditions = data_dict['conditions']
    else:
        conditions = None

    if data_dict.has_key('phone_numbers'):
        phone_numbers = data_dict['phone_numbers']
    else:
        phone_numbers = None

    if data_dict.has_key('notes'):
        notes = data_dict['notes']
    else:
        notes = None

    obj, created = CalWildfire.objects.get_or_create(
        created_fire_id = created_fire_id,
        defaults={
            'twitter_hashtag': twitter_hashtag,
            'last_scraped': datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('US/Pacific')),

            'fire_name': fire_name,
            'county': county,
            'acres_burned': acres_burned,
            'containment_percent': containment_percent,
            'date_time_started': date_time_started,
            'last_updated': last_updated,
            'administrative_unit': administrative_unit,
            'more_info': more_info,
            'fire_slug': fire_slug,
            'county_slug': county_slug,

            'location': location,

            'injuries': injuries,
            'evacuations': evacuations,
            'structures_threatened': structures_threatened,
            'structures_destroyed': structures_destroyed,

            'total_dozers': total_dozers,
            'total_helicopters': total_helicopters,
            'total_fire_engines': total_fire_engines,
            'total_fire_personnel': total_fire_personnel,
            'total_water_tenders': total_water_tenders,
            'total_airtankers': total_airtankers,
            'total_fire_crews': total_fire_crews,

            'cause': cause,
            'cooperating_agencies': cooperating_agencies,
            'road_closures': road_closures,
            'conditions': conditions,
            'phone_numbers': phone_numbers,
            'notes': notes,
        }
    )

    if not created:
        obj.last_scraped = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('US/Pacific'))
        obj.acres_burned = acres_burned
        obj.containment_percent = containment_percent
        obj.date_time_started = date_time_started
        obj.last_updated = last_updated
        obj.administrative_unit = administrative_unit
        obj.more_info = more_info

        obj.fire_slug = fire_slug
        obj.county_slug = county_slug

        obj.location = location
        obj.injuries = injuries
        obj.evacuations = evacuations
        obj.structures_threatened = structures_threatened
        obj.structures_destroyed = structures_destroyed

        obj.total_dozers = total_dozers
        obj.total_helicopters = total_helicopters
        obj.total_fire_engines = total_fire_engines
        obj.total_fire_personnel = total_fire_personnel
        obj.total_water_tenders = total_water_tenders
        obj.total_airtankers = total_airtankers
        obj.total_fire_crews =  total_fire_crews

        obj.cause = cause
        obj.cooperating_agencies = cooperating_agencies
        obj.road_closures = road_closures
        obj.conditions = conditions
        obj.road_closures = road_closures
        obj.notes = notes
        obj.save()

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

def convert_time_to_nicey_format(date_to_parse):
    ''' work crazy datetime magic that might be working '''
    los_angeles = pytz.timezone('US/Pacific')
    target_datetime = los_angeles.localize(parser.parse(date_to_parse))
    return target_datetime

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
        iterate_through_urls_to_scrape()
        self.stdout.write('\nScraping finished at %s\n' % str(datetime.datetime.now()))