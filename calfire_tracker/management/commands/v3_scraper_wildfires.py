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
from scraper_configs import TestScraper

logging.basicConfig(level=logging.DEBUG)

def retrieve_data_from_page():
    ''' save raw html from a web page locally '''
    scraper_instance =TestScraper()
    raw_html = scraper_instance.retrieve_source_html_with_mechanize('http://cdfdata.fire.ca.gov/incidents/incidents_current?pc=500')
    local_file = scraper_instance.save_source_html_to_file('incidents_current.html', raw_html)

def open_file_and_parse_to_list(local_file):
    ''' open local file, convert data table to dictionary & append to list '''
    list_of_fires = []
    target_data = BeautifulSoup(open(local_file), convertEntities=BeautifulSoup.HTML_ENTITIES)
    table_instances = target_data.findAll('table', {'class': 'incident_table'})[1:]
    for table in table_instances:
        data_dict = {}
        data_rows = table.findAll('tr')[1:]
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
        created_fire_id = '%s-%s' % (data_dict['name'], data_dict['county'])
        data_dict['created_fire_id'] = created_fire_id
        list_of_fires.append(data_dict)
    add_data_source_to(list_of_fires)

def add_data_source_to(list_of_fires):
    ''' sets data source to CalFire if no details link and sets last update to none if key not present '''
    for fire in list_of_fires:
        if 'details_source' in fire:
            pass
        else:
            fire['details_source'] = 'CalFire'
            fire['details_link'] = None
        #if 'last_update' in fire:
            #pass
        #else:
            #fire['last_update'] = None
    evaluate_whether_to_follow_details_link(list_of_fires)

def evaluate_whether_to_follow_details_link(list_of_fires):
    ''' lets query the database to compare last_update time stamps '''
    for fire in list_of_fires:
        if fire['details_source'] == 'CalFire' and fire['details_link'] is not None:
            details_scraper =TestScraper()
            raw_html = details_scraper.retrieve_source_html_with_mechanize(fire['details_link'])
            raw_details = BeautifulSoup(raw_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
            details_table = raw_details.findAll('table', {'class': 'incident_table'})
            for table in details_table:
                data_dict = {}
                data_dict['name'] = fire['name']
                data_dict['details_source'] = fire['details_source']
                data_dict['details_link'] = fire['details_link']
                data_rows = table.findAll('tr')[1:]
                for row in data_rows:
                    target_cell = row.findAll('td')
                    target_key = lowercase_remove_colon_and_replace_space_with_underscore(target_cell[0].text.encode('utf-8'))
                    target_data = target_cell[1].text.encode('utf-8')
                    data_dict[target_key] = target_data
                save_data_from_dict_to_model(data_dict)
            print fire['name'] + ' has details page and didnt reach date comparison test'

            ## DOES DETAIL PAGE NEED TO DATE COMPARISON
            ## THIS MIGHT BE GOOD PLACE TO RUN COMPARISON AGAINST POPULATED DATA THAT DISAPPEARS...

        elif fire['details_source'] == 'CalFire' and fire['details_link'] == None:
            does_fire_exist_and_is_info_new(fire)
        elif fire['details_source'] == 'Other/Inciweb':
            does_fire_exist_and_is_info_new(fire)
        else:
            does_fire_exist_and_is_info_new(fire)

def does_fire_exist_and_is_info_new(fire):
    try:
        query_date_from_database = CalWildfire.objects.get(created_fire_id=fire['created_fire_id'])
        if fire.has_key('last_update'):
            date_comparison_boolean = compare_webpage_to_database(fire['last_update'], query_date_from_database.last_updated)
            if date_comparison_boolean == True:
                print fire['name'] + ' will be updated with new info'
                save_data_from_dict_to_model(fire)
            else:
                print fire['name'] + ' doesnt have new info'
                pass
        else:
            print fire['name'] + ' doesnt have a date to compare'
            pass
    except:
        print fire['name'] + ' doesnt exist in the database'
        save_data_from_dict_to_model(fire)

def save_data_from_dict_to_model(data_dict):
    ''' save data stored in dict to models '''

    if data_dict.has_key('name'):
        fire_name = data_dict['name']
    else:
        fire_name = 'fire_name'

    if data_dict.has_key('county'):
        county = data_dict['county']
    else:
        county = None

    if data_dict.has_key('created_fire_id'):
        created_fire_id = data_dict['created_fire_id']
    else:
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

    if data_dict.has_key('details_source'):
        data_source = data_dict['details_source']
    else:
        data_source = None

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

    if data_dict.has_key('details_link'):
        more_info = data_dict['details_link']
    else:
        more_info = None

    county_slug = '%s' % (slugifyFireName(county))
    scraped_fire_slug = '%s' % (slugifyFireName(fire_name))

    # if an object with fire slug exists in the database
    if not CalWildfire.objects.filter(fire_slug=scraped_fire_slug).exists():
        fire_slug = scraped_fire_slug

    # if it does, append the county slug to the fire slug
    else:
        fire_slug = '%s-%s' % (scraped_fire_slug, county_slug)

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

    if data_dict.has_key('school_closures_'):
        school_closures = data_dict['school_closures_']
    else:
        school_closures = None

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

    last_scraped = datetime.datetime.now()

    obj, created = CalWildfire.objects.get_or_create(
        created_fire_id = created_fire_id,

        defaults={
            'twitter_hashtag': twitter_hashtag,
            'last_scraped': last_scraped,
            'data_source': data_source,
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
            'school_closures': school_closures,
            'conditions': conditions,
            'phone_numbers': phone_numbers,
            'notes': notes,
        }
    )

    #if not created and obj.last_updated == last_updated:
        #obj.last_scraped = last_scraped
        #obj.save()

    if not created:
    #else:
        obj.last_scraped = last_scraped
        obj.acres_burned = acres_burned
        obj.containment_percent = containment_percent
        obj.date_time_started = date_time_started
        obj.last_updated = last_updated
        obj.administrative_unit = administrative_unit
        obj.more_info = more_info
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
        obj.school_closures = school_closures
        obj.conditions = conditions
        obj.phone_numbers = phone_numbers
        obj.notes = notes
        obj.save()

class Command(BaseCommand):
    help = 'Scrapes California Wildfires data'
    def handle(self, *args, **options):
        self.stdout.write('\nScraping started at %s\n' % str(datetime.datetime.now()))

        #retrieve_data_from_page()
        open_file_and_parse_to_list('incidents_current.html')

        self.stdout.write('\nScraping finished at %s\n' % str(datetime.datetime.now()))

### begin helper and formatting functions ###
def lowercase_remove_colon_and_replace_space_with_underscore(string):
    ''' lowercase_remove_colon_and_replace_space_with_underscore '''
    formatted_data = string.lower().replace(':', '').replace(' ', '_').replace('_-_', '_').replace('/', '_')
    return formatted_data

def determine_if_details_link_present(target_cell):
    ''' extracts an anchor tag if present in cell, determines source & creates dictionary to add to fire '''
    target_text = target_cell[1].findAll('a')
    data_dict = {}
    if len(target_text) == 0:
        pass
    else:
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

def compare_webpage_to_database(date_from_webpage, date_from_database):
    ''' convert date to datetime, set tzinfo to pacific and compare it as UTC '''
    utc = timezone('UTC')
    pacific = pytz.timezone('US/Pacific')
    parsed_date_from_webpage = parser.parse(date_from_webpage)
    parsed_date_from_webpage = pacific.localize(parsed_date_from_webpage)
    parsed_date_from_webpage = parsed_date_from_webpage.astimezone(utc)
    if date_from_database < parsed_date_from_webpage:
        should_i_update = True
    else:
        should_i_update = False
    return should_i_update

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
            #logging.debug(target_number)
            target_number = re.search(extract_number, target_number)
            target_number = target_number.group()
            target_number = int(target_number)
            #logging.debug(target_number)

        else:
            target_number = None
            #logging.debug(target_number)
    except:
        target_number = 'exception'
        #logging.debug(target_number)

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
                #logging.debug(target_number)
                target_number = re.search(extract_number, target_number[1])
                target_number = target_number.group()
                target_number = int(target_number)
                #logging.debug(target_number)
            else:
                target_number = 100
        else:
            target_number = None
    except:
        target_number = 'exception'
    return target_number