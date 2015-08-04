from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.core.mail import send_mail, mail_admins, send_mass_mail, EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from calfire_tracker.models import CalWildfire
from django.contrib.auth.models import User
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
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

logger = logging.getLogger("calfire_tracker")

SCRAPER_VARIABLES = {
    "status": "live",
    "request_url": "http://cdfdata.fire.ca.gov/incidents/incidents_current?pc=500",
    "request_headers": {
        "From": "ckeller@scpr.org",
        "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19"
    },
}

class WildfireDataUtilities(object):

    def make_request_to(self, request_url):
        """
        make request to url and return response content
        """
        while True:
            try:
                request = requests.get(request_url, headers = SCRAPER_VARIABLES["request_headers"])
                if request.status_code == 200:
                    return request.content
                else:
                    return False
            except Exception, exception:
                logger.error("(%s) %s - %s" % (str(datetime.datetime.now()), request_url, exception))
                return False

    def make_soup(self, raw_html):
        """
        creates beautiful soup from raw html
        """
        raw_html_content = BeautifulSoup(raw_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        table_instances = raw_html_content.findAll("table", {"class": "incident_table"})
        return table_instances

    def details_link_present(self, table):
        """
        isolate links to more details
        """
        details_url = table.findAll("a")
        if len(details_url) > 0:
            if len(details_url) > 1:
                details_link = "http://cdfdata.fire.ca.gov%s" % (details_url[1]['href']).strip()
            else:
                details_link = details_url[0]['href'].strip()
        else:
            details_link = None
        return details_link

    def details_source(self, url):
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
                details_source = "Other"
        return details_source

    def string_to_dict_key(self, string):
        """
        string_to_dict_key
        """
        formatted_data = string.lower()
        formatted_data = formatted_data.replace(':', '').replace(' ', '_').replace('_-_', '_').replace('/', '_')
        return formatted_data

    def compare_webpage_to_database(self, date_from_webpage, date_from_database):
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

    def send_new_fire_email(self, fire_name, acres_burned, county, containment_percent):
        """
        send email to list when a new fire is added to the database
        """
        user_email_alert_list = []
        all_users = User.objects.all()
        for user in all_users:
            if user.username != "sdillingham":
                if user.is_active == True:
                    user_email_alert_list.append(user.email)
        email_date = datetime.datetime.now().strftime("%A, %b %d, %Y at %I:%M %p")
        email_subject = "%s in %s has been added to Fire Tracker" % (fire_name, county)
        email_message = "The %s has burned %s acres in %s and is at %s%% containment.\n\nThis fire was added to Fire Tracker on %s" % (fire_name, acres_burned, county, containment_percent, email_date)
        send_mail(email_subject, email_message, "kpccdatadesk@gmail.com", user_email_alert_list, fail_silently=True)

    def slugifyFireName(self, string):
        """
        lowercase_and_replace_space_with_dash
        """
        formatted_data = string.lower().replace(":", "-").replace(" ", "-").replace("_", "-").replace("_-_", "-").replace("/", "-")
        return formatted_data

    def hashtagifyFireName(self, string):
        """
        lowercase_and_replace_space_with_dash
        """
        formatted_data = string.title().replace(" ", "")
        return "#%s" %(formatted_data)

    def convert_time_to_nicey_format(self, date_time_parse):
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

    def convert_soup_list_to_data(self, element):
        """
        takes table row that is a list and converts it to data
        """
        for el in element:
            target_data = el.text.encode("utf-8")
            return target_data

    def extract_acres_integer(self, string_to_match):
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

    def extract_containment_amount(self, string):
        """
        runs regex on acres cell to return containment as int
        """
        extract_surrounded_number = re.compile("(\d+.)")
        string = string.replace(",", "").replace("-", "").strip()
        percent_match = re.search("%", string)
        if percent_match:
            try:
                this_match = re.findall(extract_surrounded_number, string)
                if len(this_match) == 2:
                    target_number = this_match[1].strip("%")
                    target_number = int(target_number)
                else:
                    target_number = None
            except Exception, exception:
                logger.error("(%s) %s" % (str(datetime.datetime.now()), exception))
                target_number = None
        else:
            target_number = None
        return target_number

    def extract_initial_integer(self, string_to_match):
        """
        runs regex on acres cell to return acres burned as int
        """
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

    def split_lat_lng_pairs(self, string):
        """
        splits a latitude/longitude pair and returns a list
        """
        string = string.split("/")
        lat_lng_list = string[::-1]
        return lat_lng_list


class WildfireDataClient(object):

    UTIL = WildfireDataUtilities()

    def _init(self, *args, **kwargs):
        if SCRAPER_VARIABLES["status"] == "testing":
            raw_html = "/Users/ckeller/Desktop/target.html"
            raw_html_content = BeautifulSoup(open(raw_html), convertEntities=BeautifulSoup.HTML_ENTITIES)
        else:
            request_url = SCRAPER_VARIABLES["request_url"]
            raw_html = self.UTIL.make_request_to(request_url)
            raw_html_content = BeautifulSoup(raw_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        table_instances = raw_html_content.findAll("table", {"class": "incident_table"})[1:]
        for table in table_instances:
            individual_fire = {}
            fire = self.build_fire_dict_from(table, individual_fire)
            fire["update_this_fire"] = self.does_fire_exist_and_is_info_new(fire)
            if fire["update_this_fire"] == True:
                if fire["name"] == "Shirley Fire" and fire["last_update"] == "June 20, 2014 8:30 am":
                    fire["details_source"] = "Inciweb"
                    fire["details_link"] = "http://inciweb.nwcg.gov/incident/3895/"
                    self.inciweb_details_scraper(fire)
                    self.normalize_fire_data(fire)
                elif fire["name"] == "Mason Fire" and fire["details_link"] == "http://inciweb.nwcg.gov/incident/4382/":
                    fire["details_source"] = "Inciweb"
                    fire["details_link"] = "http://inciweb.nwcg.gov/incident/4275/"
                    self.inciweb_details_scraper(fire)
                    self.normalize_fire_data(fire)
                elif fire["details_source"] == "Inciweb":
                    self.inciweb_details_scraper(fire)
                    self.normalize_fire_data(fire)
                elif fire["details_source"] == "CalFire" and fire["details_link"] == None:
                    self.normalize_fire_data(fire)
                elif fire["details_source"] == "CalFire" and fire["details_link"] != None:
                    details_link = fire["details_link"]
                    _raw_html = self.UTIL.make_request_to(fire["details_link"])
                    _table_instances = self.UTIL.make_soup(_raw_html)
                    for _table in _table_instances:
                        self.build_fire_dict_from(_table, fire)
                    fire["details_link"] = details_link
                    self.normalize_fire_data(fire)
                else:
                    self.normalize_fire_data(fire)
                logger.debug("Attempting to update %s" % (fire["name"]))
                self.save_data_from_dict_to_model(fire)
            else:
                logger.debug("%s doesn't appear to have been updated and I am skipping it" % (fire["name"]))

    def build_fire_dict_from(self, table, individual_fire):
        """
        create a dict based on a calfire table and return it
        """
        individual_fire["details_link"] = self.UTIL.details_link_present(table)
        individual_fire["details_source"] = self.UTIL.details_source(individual_fire["details_link"])
        table_row = table.findAll("tr")[1:]
        for table_cell in table_row:
            target_cell = table_cell.findAll("td")
            target_key = self.UTIL.string_to_dict_key(target_cell[0].text.encode("utf-8"))
            target_data = target_cell[1].text.encode("utf-8")
            if individual_fire.has_key(target_key):
                pass
            else:
                individual_fire[target_key] = target_data.strip("&nbsp;")
        individual_fire["created_fire_id"] = '%s-%s' % (individual_fire["name"], individual_fire["county"])
        return individual_fire

    def inciweb_details_scraper(self, fire):
        """
        pull details from inciweb details page
        """
        details_link = fire["details_link"]
        _inciweb_html = self.UTIL.make_request_to(fire["details_link"])
        _inciweb_soup = BeautifulSoup(_inciweb_html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        table_instances = _inciweb_soup.findAll('table', {'class': 'data'})
        for table in table_instances:
            instance_of_data_rows = {}
            data_rows = table.findAll('tr')[1:]
            for row in data_rows:
                target_key = self.UTIL.convert_soup_list_to_data(row.findAll('th'))
                target_key = self.UTIL.string_to_dict_key(target_key)
                target_data = self.UTIL.convert_soup_list_to_data(row.findAll('td'))
                instance_of_data_rows[target_key] = target_data
            fire.update(instance_of_data_rows)
        long_lat = _inciweb_soup.findAll(text=re.compile("latitude"))
        if len(long_lat) > 0:
            fire["long_lat"] = long_lat[0].strip()
        if fire.has_key("size"):
            acres_burned = fire["size"]
        else:
            acres_burned = None
        if fire.has_key("percent_of_perimeter_contained"):
            percent_contained = fire["percent_of_perimeter_contained"]
        elif fire.has_key("percent_contained"):
            percent_contained = fire["percent_contained"]
        else:
            percent_contained = None
        fire["acres_burned_containment"] = "%s -%scontained" % (acres_burned, percent_contained)
        remarks_list = []
        try:
            remarks = "%s" % (fire["remarks"])
            events = "%s" % (fire["significant_events"])
            behavior = "%s" % (fire["fire_behavior"])
            fuel = "Fuel for the fire includes %s." % (fire["fuels_involved"])
            terrain = "Terrain difficulty is %s." % (fire["terrain_difficulty"])
        except Exception, exception:
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
        fire["details_link"] = details_link
        try:
            remarks = " ".join(remarks_list)
            fire["remarks"] = remarks
        except Exception, exception:
            pass
        return fire

    def does_fire_exist_and_is_info_new(self, fire):
        """
        checks date on newly acquired fire against the database
        """
        try:
            query_date_from_database = CalWildfire.objects.get(created_fire_id=fire["created_fire_id"])
            if fire.has_key("last_update"):
                return self.UTIL.compare_webpage_to_database(fire["last_update"], query_date_from_database.last_updated)
            elif fire.has_key("last_updated"):
                return self.UTIL.compare_webpage_to_database(fire["last_updated"], query_date_from_database.last_updated)
            else:
                return True
        except ObjectDoesNotExist, exception:
            logger.error("%s - %s" % (exception, fire))
            return True
        except Exception, exception:
            logger.error("%s - %s" % (exception, fire))
            raise

    def normalize_fire_data(self, fire):
        """
        this is a rigorous attempt to normalize scraped data
        """

        if fire.has_key("name"):
            if "Fire" in fire["name"]:
                fire["name"] = fire["name"]
            elif "fire" in fire["name"]:
                fire["name"] = fire["name"]
            else:
                fire["name"] = "%s Fire" % (fire["name"])
        else:
            fire["name"] = "fire_name"

        if fire.has_key("county"):
            fire["county"] = fire["county"]
            if fire["county"] == "Los Angele":
                fire["county"] = "Los Angeles County"
        else:
            fire["county"] = None

        if fire.has_key("created_fire_id"):
            fire["created_fire_id"] = fire["created_fire_id"]
        else:
            fire["created_fire_id"] = "%s-%s" % (fire["name"], fire["county"])

        fire["twitter_hashtag"] = self.UTIL.hashtagifyFireName(fire["name"])

        # if fire.has_key("estimated_containment"):
        #     acres_burned = self.UTIL.extract_acres_integer(fire["estimated_containment"])
        #     containment_percent = self.UTIL.extract_containment_amount(fire["estimated_containment"])

        if fire.has_key("acres_burned_containment"):
            fire["acres_burned"] = self.UTIL.extract_acres_integer(fire["acres_burned_containment"])
            fire["containment_percent"] = self.UTIL.extract_containment_amount(fire["acres_burned_containment"])
        elif fire.has_key("containment"):
            fire["acres_burned"] = self.UTIL.extract_acres_integer(fire["containment"])
            fire["containment_percent"] = self.UTIL.extract_containment_amount(fire["containment"])
        else:
            fire["acres_burned"] = None
            fire["containment_percent"] = None

        if fire.has_key("details_source"):
            fire["details_source"] = fire["details_source"]
        else:
            fire["details_source"] = None

        if fire.has_key("date_time_started"):
            fire["date_time_started"] = self.UTIL.convert_time_to_nicey_format(fire["date_time_started"])
            fire["year"] = fire["date_time_started"].year
        elif fire.has_key("date_started"):
            fire["date_time_started"] = self.UTIL.convert_time_to_nicey_format(fire["date_started"])
            fire["year"] = fire["date_time_started"].year
        else:
            fire["date_time_started"] = None
            fire["year"] = None

        if fire.has_key("last_updated"):
            fire["last_updated"] = self.UTIL.convert_time_to_nicey_format(fire["last_updated"])
        elif fire.has_key("last_update"):
            fire["last_updated"] = self.UTIL.convert_time_to_nicey_format(fire["last_update"])
        else:
            fire["last_updated"] = datetime.datetime.now()

        if fire.has_key("administrative_unit"):
            fire["administrative_unit"] = fire["administrative_unit"]
        else:
            fire["administrative_unit"] = None

        if fire.has_key("details_link"):
            fire["details_link"] = fire["details_link"]
        else:
            fire["details_link"] = None

        if fire.has_key("location"):
            fire["location"] = fire["location"].title()
        else:
            fire["location"] = None

        if fire.has_key("long_lat"):
            try:
                location_list = self.UTIL.split_lat_lng_pairs(fire["long_lat"])
                try:
                    fire["location_latitude"] = location_list[0].replace("latitude", "").strip()
                    fire["location_longitude"] = location_list[1].replace("longitude", "").strip()
                    fire["location_geocode_error"] = False
                except:
                    fire["location_latitude"] = location_list[0]
                    fire["location_longitude"] = location_list[1]
                    fire["location_geocode_error"] = False
            except:
                fire["location_latitude"] = None
                fire["location_longitude"] = None
                fire["location_geocode_error"] = True
        else:
            fire["location_latitude"] = None
            fire["location_longitude"] = None
            fire["location_geocode_error"] = True

        if fire.has_key("injuries"):
            fire["injuries"] = self.UTIL.extract_initial_integer(fire["injuries"])
        else:
            fire["injuries"] = None

        if fire.has_key("evacuations"):
            fire["evacuations"] = fire["evacuations"]
        else:
            fire["evacuations"] = None

        if fire.has_key("structures_threatened"):
            fire["structures_threatened"] = fire["structures_threatened"]
        else:
            fire["structures_threatened"] = None

        if fire.has_key("structures_destroyed"):
            fire["structures_destroyed"] = fire["structures_destroyed"]
        else:
            fire["structures_destroyed"] = None

        if fire.has_key("total_dozers"):
            fire["total_dozers"] = self.UTIL.extract_initial_integer(fire["total_dozers"])
        else:
            fire["total_dozers"] = None

        if fire.has_key("total_helicopters"):
            fire["total_helicopters"] = self.UTIL.extract_initial_integer(fire["total_helicopters"])
        else:
            fire["total_helicopters"] = None

        if fire.has_key("total_fire_engines"):
            fire["total_fire_engines"] = self.UTIL.extract_initial_integer(fire["total_fire_engines"])
        else:
            fire["total_fire_engines"] = None

        if fire.has_key("total_fire_personnel"):
            fire["total_fire_personnel"] = self.UTIL.extract_initial_integer(fire["total_fire_personnel"])
        else:
            fire["total_fire_personnel"] = None

        if fire.has_key("total_water_tenders"):
            fire["total_water_tenders"] = self.UTIL.extract_initial_integer(fire["total_water_tenders"])
        else:
            fire["total_water_tenders"] = None

        if fire.has_key("total_airtankers"):
            fire["total_airtankers"] = self.UTIL.extract_initial_integer(fire["total_airtankers"])
        else:
            fire["total_airtankers"] = None

        if fire.has_key("total_fire_crews"):
            fire["total_fire_crews"] = self.UTIL.extract_initial_integer(fire["total_fire_crews"])
        else:
            fire["total_fire_crews"] = None

        if fire.has_key("cause"):
            fire["cause"] = fire["cause"]
        else:
            fire["cause"] = None

        if fire.has_key("cooperating_agencies"):
            fire["cooperating_agencies"] = fire["cooperating_agencies"]
        else:
            fire["cooperating_agencies"] = None

        if fire.has_key("road_closures_"):
            fire["road_closures_"] = fire["road_closures_"]
        else:
            fire["road_closures_"] = None

        if fire.has_key("school_closures_"):
            fire["school_closures_"] = fire["school_closures_"]
        else:
            fire["school_closures_"] = None

        if fire.has_key("conditions"):
            fire["conditions"] = fire["conditions"]
        else:
            fire["conditions"] = None

        if fire.has_key("current_situation"):
            fire["current_situation"] = fire["current_situation"]
        elif fire.has_key("remarks"):
            fire["current_situation"] = fire["remarks"]
        else:
            fire["current_situation"] = None

        if fire.has_key("phone_numbers"):
            fire["phone_numbers"] = fire["phone_numbers"]
        else:
            fire["phone_numbers"] = None

        fire["last_scraped"] = datetime.datetime.now()

        fire["county_slug"] = self.UTIL.slugifyFireName(fire["county"])

        fire["fire_slug"] = self.UTIL.slugifyFireName(fire["name"])

        fire["naming_slug"] = "%s-%s" % (fire["fire_slug"], fire["county_slug"])

        return fire

    def save_data_from_dict_to_model(self, fire):
        """
        save data stored in dict to models
        """

        if not CalWildfire.objects.filter(fire_slug = fire["fire_slug"]).exists():
            fire_slug = fire["naming_slug"]
        else:
            fire_slug = fire["naming_slug"]

        if fire["created_fire_id"] == "South Napa Earthquake-Napa County":
            pass

        else:
            logger.debug(fire)
            try:
                obj, created = CalWildfire.objects.get_or_create(
                    created_fire_id = fire["created_fire_id"],
                    defaults={
                        "twitter_hashtag": fire["twitter_hashtag"],
                        "last_scraped": fire["last_scraped"],
                        "data_source": fire["details_source"],
                        "fire_name": fire["name"],
                        "county": fire["county"],
                        "acres_burned": fire["acres_burned"],
                        "containment_percent": fire["containment_percent"],
                        "date_time_started": fire["date_time_started"],
                        "last_updated": fire["last_updated"],
                        "administrative_unit": fire["administrative_unit"],
                        "more_info": fire["details_link"],
                        "fire_slug": fire["fire_slug"],
                        "county_slug": fire["county_slug"],
                        "year": fire["year"],
                        "location": fire["location"],
                        "location_latitude": fire["location_latitude"],
                        "location_longitude": fire["location_longitude"],
                        "location_geocode_error": fire["location_geocode_error"],
                        "injuries": fire["injuries"],
                        "evacuations": fire["evacuations"],
                        "structures_threatened": fire["structures_threatened"],
                        "structures_destroyed": fire["structures_destroyed"],
                        "total_dozers": fire["total_dozers"],
                        "total_helicopters": fire["total_helicopters"],
                        "total_fire_engines": fire["total_fire_engines"],
                        "total_fire_personnel": fire["total_fire_personnel"],
                        "total_water_tenders": fire["total_water_tenders"],
                        "total_airtankers": fire["total_airtankers"],
                        "total_fire_crews": fire["total_fire_crews"],
                        "cause": fire["cause"],
                        "cooperating_agencies": fire["cooperating_agencies"],
                        "road_closures": fire["road_closures_"],
                        "school_closures": fire["school_closures_"],
                        "conditions": fire["conditions"],
                        "current_situation": fire["current_situation"],
                        "phone_numbers": fire["phone_numbers"],
                    }
                )
                if not created and obj.update_lockout == True:
                    pass

                elif created:
                    if SCRAPER_VARIABLES["status"] != "testing":
                        self.UTIL.send_new_fire_email(fire_name, acres_burned, county, containment_percent)
                else:
                    try:
                        #prev_obj = obj
                        #self.UTIL.send_new_fire_email(prev_obj, fire)

                        obj.last_scraped = fire["last_scraped"]

                        if fire["acres_burned"] == None:
                            obj.acres_burned = obj.acres_burned
                        else:
                            obj.acres_burned = fire["acres_burned"]

                        if fire["containment_percent"] == None:
                            obj.containment_percent = obj.containment_percent
                        else:
                            obj.containment_percent = fire["containment_percent"]

                        obj.last_updated = fire["last_updated"]

                        obj.administrative_unit = fire["administrative_unit"]

                        if fire["details_link"] == None:
                            obj.more_info = obj.more_info
                        else:
                            obj.more_info = fire["details_link"]

                        obj.location = fire["location"]
                        obj.location_latitude = fire["location_latitude"]
                        obj.location_longitude = fire["location_longitude"]
                        obj.location_geocode_error = fire["location_geocode_error"]
                        obj.injuries = fire["injuries"]
                        obj.evacuations = fire["evacuations"]
                        obj.structures_threatened = fire["structures_threatened"]
                        obj.structures_destroyed = fire["structures_destroyed"]
                        obj.total_dozers = fire["total_dozers"]
                        obj.total_helicopters = fire["total_helicopters"]
                        obj.total_fire_engines = fire["total_fire_engines"]
                        obj.total_fire_personnel = fire["total_fire_personnel"]
                        obj.total_water_tenders = fire["total_water_tenders"]
                        obj.total_airtankers = fire["total_airtankers"]
                        obj.total_fire_crews =  fire["total_fire_crews"]
                        obj.cause = fire["cause"]
                        obj.cooperating_agencies = fire["cooperating_agencies"]
                        obj.road_closures = fire["road_closures_"]
                        obj.school_closures = fire["school_closures_"]
                        obj.conditions = fire["conditions"]
                        obj.current_situation = fire["current_situation"]
                        obj.phone_numbers = fire["phone_numbers"]
                        obj.save()
                    except Exception, exception:
                        logger.error("%s - %s" % (exception, fire["details_link"]))
            except Exception, exception:
                logger.error("%s - %s" % (exception, fire["details_link"]))

if __name__ == "__main__":
    task_run = WildfireDataClient()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
