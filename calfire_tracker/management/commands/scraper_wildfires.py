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


#logger = logging.getLogger("root")
#logging.basicConfig(
    #format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    #level=logging.DEBUG
#)

logger = logging.getLogger('calfire_tracker')

scraper_variables = {
    "status": "live",
    "request_url": "http://cdfdata.fire.ca.gov/incidents/incidents_current?pc=500",
    "request_headers": {
        "From": "ckeller@scpr.org",
        "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19"
    },
}


class Command(BaseCommand):
    """
    If testing, we'll store html locally
    If live, we'll make a request to the page
    """
    help = 'Scrapes California Wildfires data'
    def handle(self, *args, **options):
        if scraper_variables["status"] == "testing":
            raw_html = make_request_to(scraper_variables["request_url"])
            with open("wildfire_test.html", "wb", buffering=0) as new_file:
                new_file.write(raw_html)
            new_file.close()
            process("wildfire_test.html")
        elif scraper_variables["status"] == "live":
            raw_html = make_request_to(scraper_variables["request_url"])
            process(raw_html)
        else:
            pass
        self.stdout.write('\nScraping finished at %s\n' % str(datetime.datetime.now()))


def make_request_to(url):
    """
    make request to url and return response content
    """
    while True:
        try:
            #time.sleep(60*1)
            request = requests.get(url, headers=scraper_variables["request_headers"])
            if request.status_code == 200:
                raw_html = request.content
            else:
                raw_html = None
            return raw_html
        except Exception, exception:
            logger.error("(%s) %s - %s" % (str(datetime.datetime.now()), url, exception))
            time.sleep(60*10)


def process(raw_html):
    """
    process the raw_html
    """
    if scraper_variables["status"] == "testing":
        raw_html_content = BeautifulSoup(open(raw_html), convertEntities=BeautifulSoup.HTML_ENTITIES)
    else:
        raw_html_content = BeautifulSoup(raw_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    list_of_fires = []
    table_instances = raw_html_content.findAll("table", {"class": "incident_table"})[1:]
    for table in table_instances:
        individual_fire = {}
        individual_fire["details_link"] = details_link_present(table)
        individual_fire["details_source"] = details_source(individual_fire["details_link"])
        table_row = table.findAll("tr")[1:]
        for table_cell in table_row:
            target_cell = table_cell.findAll("td")
            target_key = string_to_dict_key(target_cell[0].text.encode('utf-8'))
            target_data = target_cell[1].text.encode('utf-8')
            keep_first_instance_of(individual_fire, target_key, target_data)
        individual_fire['created_fire_id'] = '%s-%s' % (individual_fire['name'], individual_fire['county'])

        """
        ## PAIN POINT
        ## round back around to check on last update
        """

        logger.debug(individual_fire)
        list_of_fires.append(individual_fire)
    follow_details_link(list_of_fires)


def string_to_dict_key(string):
    """
    string_to_dict_key
    """
    formatted_data = string.lower()
    formatted_data = formatted_data.replace(':', '')
    formatted_data = formatted_data.replace(' ', '_')
    formatted_data = formatted_data.replace('_-_', '_')
    formatted_data = formatted_data.replace('/', '_')
    return formatted_data


def details_link_present(table):
    """
    isolate links to more details
    """
    details_url = table.findAll("a")
    if len(details_url) > 0:
        if len(details_url) > 1:
            details_link = "http://cdfdata.fire.ca.gov%s" % (details_url[1]['href'])
        else:
            details_link = details_url[0]['href']
    else:
        details_link = None
    return details_link


def details_source(url):
    """
    isolate data source
    """
    if url is None:
        details_source = "CalFire"
    else:
        inciweb_match = re.search("inciweb", url)
        riverside_fd_match = re.search("rvcfire.org/_Layouts/Incident", url)
        cal_fire_match = re.search("http://cdfdata.fire.ca.gov/incidents", url)
        if inciweb_match:
            details_source = "Inciweb"
        elif riverside_fd_match:
            details_source = "Riverside County Fire Department"
        elif cal_fire_match:
            details_source = "CalFire"
        else:
            details_source = 'Other'
    return details_source


def keep_first_instance_of(target_dict, target_key, target_data):
    """
    keeps first instance of a key and keeps from being overwritten
    """
    if target_dict.has_key(target_key):
        pass
    else:
        target_dict[target_key] = target_data.strip("&nbsp;")


def follow_details_link(list_of_fires):
    """
    pull indepth details from page
    """
    for fire in list_of_fires:

        """
        """
        ## outlier issue I need to fix
        if fire["name"] == "Shirley Fire" and fire["last_update"] == "June 20, 2014 8:30 am":
            fire["details_source"] = "Inciweb"
            fire["details_link"] = "http://inciweb.nwcg.gov/incident/3895/"
            print fire["name"], fire["details_source"], fire["details_link"]
            inciweb_details_scraper(fire)
        """
        """

        if fire["details_source"] == "CalFire" and fire["details_link"] is not None:
            time.sleep(20)
            calfire_data = make_request_to(fire['details_link'])
            raw_html_content = BeautifulSoup(calfire_data)
            table_instances = raw_html_content.findAll('table', {'class': 'incident_table'})
            for table in table_instances:
                fire["details_link"] = details_link_present(table)
                fire["details_source"] = details_source(fire["details_link"])
                table_row = table.findAll("tr")[1:]
                for table_cell in table_row:
                    target_cell = table_cell.findAll("td")
                    target_key = string_to_dict_key(target_cell[0].text.encode('utf-8'))
                    target_data = target_cell[1].text.encode('utf-8')
                    keep_first_instance_of(fire, target_key, target_data)
            does_fire_exist_and_is_info_new(fire)
        elif fire['details_source'] == 'CalFire' and fire['details_link'] == None:
            does_fire_exist_and_is_info_new(fire)
        elif fire['details_source'] == 'Riverside County Fire Department':
            does_fire_exist_and_is_info_new(fire)
        elif fire['details_source'] == 'Other':
            does_fire_exist_and_is_info_new(fire)
        elif fire['details_source'] == 'Inciweb':
            inciweb_details_scraper(fire)
        else:
            does_fire_exist_and_is_info_new(fire)


def inciweb_details_scraper(fire):
    """
    pull details from inciweb details page
    """

    inciweb_data = make_request_to(fire['details_link'])
    raw_html_content = BeautifulSoup(inciweb_data)

    """
    ## PAIN POINT
    ## determine how to access text at the top of the inciweb page
    """

    table_instances = raw_html_content.findAll('table', {'class': 'data'})
    for table in table_instances:
        instance_of_data_rows = {}
        data_rows = table.findAll('tr')[1:]
        for row in data_rows:
            target_key = convert_soup_list_to_data(row.findAll('th'))
            target_key = string_to_dict_key(target_key)
            target_data = convert_soup_list_to_data(row.findAll('td'))
            instance_of_data_rows[target_key] = target_data
        fire.update(instance_of_data_rows)
    construct_inciweb_narrative(fire)


def construct_inciweb_narrative(fire):
    """
    combines narrative paragraphs into one string for later parsing for data points
    """

    try:
        acres_burned = fire['size']
        percent_contained = fire['percent_contained']

    except:
        acres_burned = None
        percent_contained = None
    fire['acres_burned_containment'] = '%s -%scontained' % (acres_burned, percent_contained)
    remarks_list = []

    try:
        remarks = '%s' % (fire['remarks'])
        events = '%s' % (fire['significant_events'])
        behavior = '%s' % (fire['fire_behavior'])
        fuel = 'Fuel for the fire includes %s.' % (fire['fuels_involved'])
        terrain = 'Terrain difficulty is %s.' % (fire['terrain_difficulty'])

    except Exception, exception:
        logger.error("(%s) %s" % (str(datetime.datetime.now()), exception))
        remarks = None
        events = None
        behavior = None
        fuel = None
        terrain = None
    remarks_list.append(remarks)
    remarks_list.append(events)
    remarks_list.append(behavior)
    remarks_list.append(fuel)
    remarks_list.append(terrain)

    try:
        remarks = ' '.join(remarks_list)
        fire['remarks'] = remarks

    except Exception, exception:
        logger.error("(%s) %s" % (str(datetime.datetime.now()), exception))
        pass

    logger.debug(fire)
    does_fire_exist_and_is_info_new(fire)


def does_fire_exist_and_is_info_new(fire):
    """
    checks date on newly acquired fire against the database
    """
    try:
        query_date_from_database = CalWildfire.objects.get(created_fire_id=fire["created_fire_id"])
        if fire.has_key("last_update"):
            fire["update_this_fire"] = compare_webpage_to_database(fire["last_update"], query_date_from_database.last_updated)
            decide_to_save_or_not(fire)
        elif fire.has_key("last_updated"):
            fire["update_this_fire"] = compare_webpage_to_database(fire["last_updated"], query_date_from_database.last_updated)
            decide_to_save_or_not(fire)
        else:
            fire["update_this_fire"] = True
            save_data_from_dict_to_model(fire)
    except Exception, exception:
        logger.error("(%s) %s" % (str(datetime.datetime.now()), exception))
        save_data_from_dict_to_model(fire)

def decide_to_save_or_not(fire):
    ''' final determination on whether to save '''
    if fire['update_this_fire'] == True:
        save_data_from_dict_to_model(fire)
    else:
        pass

def save_data_from_dict_to_model(fire):
    """
    save data stored in dict to models
    """

    print fire

    if fire.has_key("name"):
        fire_name = fire["name"]
    else:
        fire_name = "fire_name"

    if fire.has_key("county"):
        county = fire["county"]
    else:
        county = None

    if fire.has_key("created_fire_id"):
        created_fire_id = fire["created_fire_id"]
    else:
        created_fire_id = "%s-%s" % (fire_name, county)

    twitter_hashtag = "#%s" % (hashtagifyFireName(fire_name))

    if fire.has_key("estimated_containment"):
        acres_burned = extract_acres_integer(fire["estimated_containment"])
        containment_percent = extract_containment_amount(fire["estimated_containment"])
    elif fire.has_key("acres_burned_containment"):
        acres_burned = extract_acres_integer(fire["acres_burned_containment"])
        containment_percent = extract_containment_amount(fire["acres_burned_containment"])
    elif fire.has_key("containment"):
        acres_burned = extract_acres_integer(fire["containment"])
        containment_percent = extract_containment_amount(fire["containment"])
    else:
        acres_burned = None
        containment_percent = 100

    if fire.has_key("details_source"):
        data_source = fire["details_source"]
    else:
        data_source = None

    if fire.has_key("date_time_started"):
        date_time_started = convert_time_to_nicey_format(fire["date_time_started"])
        year = date_time_started.year
    elif fire.has_key("date_started"):
        date_time_started = convert_time_to_nicey_format(fire["date_started"])
        year = date_time_started.year
    else:
        date_time_started = None
        year = None

    if fire.has_key("last_updated"):
        last_updated = convert_time_to_nicey_format(fire["last_updated"])
    elif fire.has_key("last_update"):
        last_updated = convert_time_to_nicey_format(fire["last_update"])
    else:
        last_updated = datetime.datetime.now()

    if fire.has_key("administrative_unit"):
        administrative_unit = fire["administrative_unit"]
    else:
        administrative_unit = None

    if fire.has_key("details_link"):
        more_info = fire["details_link"]
    else:
        more_info = None

    if fire.has_key("location"):
        location = titlecase(fire["location"])
    else:
        location = None

    if fire.has_key("long_lat"):
        try:
            location_list = split_lat_lng_pairs(fire["long_lat"])
            location_latitude = location_list[0]
            location_longitude = location_list[1]
            location_geocode_error = False
        except:
            location_latitude = None
            location_longitude = None
            location_geocode_error = True
    else:
        location_latitude = None
        location_longitude = None
        location_geocode_error = True

    if fire.has_key("injuries"):
        injuries = extract_initial_integer(fire["injuries"])
    else:
        injuries = None

    if fire.has_key("evacuations"):
        evacuations = fire["evacuations"]
    else:
        evacuations = None

    if fire.has_key("structures_threatened"):
        structures_threatened = fire["structures_threatened"]
    else:
        structures_threatened = None

    if fire.has_key("structures_destroyed"):
        structures_destroyed = fire["structures_destroyed"]
    else:
        structures_destroyed = None

    if fire.has_key("total_dozers"):
        total_dozers = extract_initial_integer(fire["total_dozers"])
    else:
        total_dozers = None

    if fire.has_key("total_helicopters"):
        total_helicopters = extract_initial_integer(fire["total_helicopters"])
    else:
        total_helicopters = None

    if fire.has_key("total_fire_engines"):
        total_fire_engines = extract_initial_integer(fire["total_fire_engines"])
    else:
        total_fire_engines = None

    if fire.has_key("total_fire_personnel"):
        total_fire_personnel = extract_initial_integer(fire["total_fire_personnel"])
    else:
        total_fire_personnel = None

    if fire.has_key("total_water_tenders"):
        total_water_tenders = extract_initial_integer(fire["total_water_tenders"])
    else:
        total_water_tenders = None

    if fire.has_key("total_airtankers"):
        total_airtankers = extract_initial_integer(fire["total_airtankers"])
    else:
        total_airtankers = None

    if fire.has_key("total_fire_crews"):
        total_fire_crews = extract_initial_integer(fire["total_fire_crews"])
    else:
        total_fire_crews = None

    if fire.has_key("cause"):
        cause = fire["cause"]
    else:
        cause = None

    if fire.has_key("cooperating_agencies"):
        cooperating_agencies = fire["cooperating_agencies"]
    else:
        cooperating_agencies = None

    if fire.has_key("road_closures_"):
        road_closures = fire["road_closures_"]
    else:
        road_closures = None

    if fire.has_key("school_closures_"):
        school_closures = fire["school_closures_"]
    else:
        school_closures = None

    if fire.has_key("conditions"):
        conditions = fire["conditions"]
    else:
        conditions = None

    if fire.has_key("current_situation"):
        current_situation = fire["current_situation"]
    elif fire.has_key("remarks"):
        current_situation = fire["remarks"]
    else:
        current_situation = None

    if fire.has_key("phone_numbers"):
        phone_numbers = fire["phone_numbers"]
    else:
        phone_numbers = None

    last_scraped = datetime.datetime.now()

    county_slug = "%s" % (slugifyFireName(county))

    scraped_fire_slug = "%s" % (slugifyFireName(fire_name))

    if not CalWildfire.objects.filter(fire_slug=scraped_fire_slug).exists():
        fire_slug = scraped_fire_slug
    else:
        fire_slug = "%s-%s" % (scraped_fire_slug, county_slug)

    obj, created = CalWildfire.objects.get_or_create(
        created_fire_id = created_fire_id,
        defaults={
            "twitter_hashtag": twitter_hashtag,
            "last_scraped": last_scraped,
            "data_source": data_source,
            "fire_name": fire_name,
            "county": county,
            "acres_burned": acres_burned,
            "containment_percent": containment_percent,
            "date_time_started": date_time_started,
            "last_updated": last_updated,
            "administrative_unit": administrative_unit,
            "more_info": more_info,
            "fire_slug": fire_slug,
            "county_slug": county_slug,
            "year": year,
            "location": location,
            "location_latitude": location_latitude,
            "location_longitude": location_longitude,
            "location_geocode_error": location_geocode_error,
            "injuries": injuries,
            "evacuations": evacuations,
            "structures_threatened": structures_threatened,
            "structures_destroyed": structures_destroyed,
            "total_dozers": total_dozers,
            "total_helicopters": total_helicopters,
            "total_fire_engines": total_fire_engines,
            "total_fire_personnel": total_fire_personnel,
            "total_water_tenders": total_water_tenders,
            "total_airtankers": total_airtankers,
            "total_fire_crews": total_fire_crews,
            "cause": cause,
            "cooperating_agencies": cooperating_agencies,
            "road_closures": road_closures,
            "school_closures": school_closures,
            "conditions": conditions,
            "current_situation": current_situation,
            "phone_numbers": phone_numbers,
        }
    )

    if not created and obj.update_lockout == True:
        pass

    elif created:
        send_new_fire_email(fire_name, acres_burned, county, containment_percent)

    else:
        obj.last_scraped = last_scraped
        obj.acres_burned = acres_burned
        obj.containment_percent = containment_percent
        #obj.date_time_started = date_time_started
        obj.last_updated = last_updated
        obj.administrative_unit = administrative_unit
        obj.more_info = more_info
        obj.location = location
        obj.location_latitude = location_latitude
        obj.location_longitude = location_longitude
        obj.location_geocode_error = location_geocode_error
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
        obj.current_situation = current_situation
        obj.phone_numbers = phone_numbers
        obj.save()


### begin helper and formatting functions
def send_new_fire_email(fire_name, acres_burned, county, containment_percent):
    """
    send email to list when a new fire is added to the database
    """
    email_date = datetime.datetime.now().strftime("%A, %b %d, %Y at %I:%M %p")
    email_subject = '%s in %s has been added to Fire Tracker' % (fire_name, county)
    email_message = 'The %s has burned %s acres in %s and is at %s%% containment.\n\nThis fire was added to Fire Tracker on %s' % (fire_name, acres_burned, county, containment_percent, email_date)
    send_mail(email_subject, email_message, 'kpccdatadesk@gmail.com', [
        'ckeller@scpr.org',
        'Ezassenhaus@scpr.org',
        'mroe@scpr.org',
        'brian.frank@scpr.org',
    ], fail_silently=True)


def slugifyFireName(string):
    """
    lowercase_and_replace_space_with_dash
    """
    formatted_data = string.lower().replace(":", "-").replace(" ", "-").replace("_", "-").replace("_-_", "-").replace("/", "-")
    return formatted_data


def hashtagifyFireName(string):
    """
    lowercase_and_replace_space_with_dash
    """
    formatted_data = titlecase(string).replace(" ", "")
    return formatted_data


def convert_time_to_nicey_format(date_time_parse):
    """
    work crazy datetime magic that might be working.
    based on http://stackoverflow.com/questions/17193228/python-twitter-api-tweet-timestamp-convert-from-utc-to-est
    """
    date_time_parse = date_time_parse.strip("&nbsp;")
    utc = timezone("UTC")
    pacific = pytz.timezone("US/Pacific")
    date_time_parse = parser.parse(date_time_parse)
    pacificizd_date_time_parse = pacific.localize(date_time_parse)
    return pacificizd_date_time_parse


def compare_webpage_to_database(date_from_webpage, date_from_database):
    """
    convert date to datetime, set tzinfo to pacific and compare it as UTC
    """
    date_from_webpage = date_from_webpage.strip("&nbsp;")
    utc = timezone("UTC")
    pacific = pytz.timezone("US/Pacific")
    parsed_date_from_webpage = parser.parse(date_from_webpage)
    parsed_date_from_webpage = pacific.localize(parsed_date_from_webpage)
    parsed_date_from_webpage = parsed_date_from_webpage.astimezone(utc)
    if date_from_database < parsed_date_from_webpage:
        should_i_update = True
    else:
        should_i_update = False
    return should_i_update


def convert_soup_list_to_data(element):
    """
    takes table row that is a list and converts it to data
    """
    for el in element:
        target_data = el.text.encode("utf-8")
        return target_data


def extract_acres_integer(string_to_match):
    """
    runs regex on acres cell to return acres burned as int
    """
    number_check = re.compile("\d+\sacres")
    extract_acreage = re.compile("\d+\sacres")
    extract_number = re.compile("^\d+")
    match = re.search(number_check, string_to_match)
    try:
        if match:
            target_number = string_to_match.replace(",", "")
            target_number = re.search(extract_acreage, target_number).group()
            target_number = re.search(extract_number, target_number).group()
            target_number = int(target_number)
        else:
            target_number = None
    except Exception, exception:
        logger.error("(%s) %s" % (str(datetime.datetime.now()), exception))
        target_number = "exception"
    return target_number


def extract_initial_integer(string_to_match):
    """
    runs regex on acres cell to return acres burned as int
    """
    print string_to_match
    number_check = re.compile("^\d+")
    extract_number = re.compile("\d+")
    match = re.search(number_check, string_to_match)
    try:
        if match:
            target_number = string_to_match.replace(",", "")
            target_number = re.search(extract_number, target_number)
            target_number = target_number.group()
            target_number = int(target_number)
        else:
            target_number = None
    except Exception, exception:
        logger.error("(%s) %s" % (str(datetime.datetime.now()), exception))
        target_number = "exception"
    return target_number


def split_lat_lng_pairs(string):
    """
    splits a latitude/longitude pair and returns a list
    """
    string = string.split("/")
    string = string[::-1]
    return string


def extract_containment_amount(string_to_match):
    """
    runs regex on acres cell to return containment as int
    """
    extract_number = re.compile("\d+")
    determine_hyphen = re.compile("-")
    percent_match = re.search("%", string_to_match)
    try:
        if percent_match:
            hyphen_match = re.search(determine_hyphen, string_to_match)
            if hyphen_match:
                target_number = re.split("-", string_to_match)
                target_number = re.search(extract_number, target_number[1])
                target_number = target_number.group()
                target_number = int(target_number)
            else:
                target_number = 100
        else:
            target_number = None
    except Exception, exception:
        logger.error("(%s) %s" % (str(datetime.datetime.now()), exception))
        target_number = "exception"
    return target_number