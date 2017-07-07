#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.core.mail import send_mail, mail_admins, send_mass_mail, EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from calfire_tracker.models import WildfireSource, CalWildfire
from calfire_tracker.utils_requests import Requester
from calfire_tracker.utils_data import Saver
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


class Prepper(object):


    def has_calfire_link(self, item):
        """
        isolate links to more details
        """
        link = item.findAll("a")
        if len(link) == 0:
            url = None
        elif len(link) == 1:
            url = link[0]["href"].strip()
        else:
            url = link[1]["href"].strip()
        if url:
            is_inciweb = re.search("inciweb", url)
            is_riverside = re.search("rvcfire", url)
            if is_inciweb:
                output = None
            elif is_riverside:
                output = None
            else:
                output = "http://www.fire.ca.gov%s" % (url)
        else:
            output = None
        return output


    def tablerow_to_dicts(self, table_row, dict):
        for table_cell in table_row:
            target_cell = table_cell.findAll("td")
            key = self.string_to_dict_key(target_cell[0].text.encode("utf-8"))
            value = target_cell[1].text.encode("utf-8")
            if dict.has_key(key):
                pass
            else:
                dict[key] = value.strip("&nbsp;")
                dict["created_fire_id"] = '%s-%s' % (dict["name"], dict["county"])
        return dict


    def string_to_dict_key(self, string):
        """
        converts a string_to_dict_key
        """
        if string is not None:
            return string.strip().lower().replace(":", "").replace(" ", "_").replace("_-_", "_").replace("/", "_")
        else:
            return False


    def fire_exists_and_is_new(self, fire):
        """
        checks date on newly acquired fire against the database
        """
        utc = timezone("UTC")
        pacific = pytz.timezone("US/Pacific")
        try:
            obj = CalWildfire.objects.get(created_fire_id=fire["created_fire_id"])
            if fire.has_key("last_update"):
                acquired_date = parser.parse(fire["last_update"].strip("&nbsp;"))
                localized_date = pacific.localize(acquired_date)
                utc_date = localized_date.astimezone(utc)
                if obj.last_updated < utc_date:
                    return True
                else:
                    return False
            elif fire.has_key("last_updated"):
                acquired_date = parser.parse(fire["last_updated"].strip("&nbsp;"))
                localized_date = pacific.localize(acquired_date)
                utc_date = localized_date.astimezone(utc)
                if obj.last_updated < utc_date:
                    return True
                else:
                    return False
            else:
                return True
        except ObjectDoesNotExist, exception:
            # logger.error("%s - Adding %s to the database" % (exception, fire["name"]))
            return True


    def give_fire(self):
        return {
            # "fire_name": None,
            # "county": None,
            # "fire_slug": None,
            # "county_slug": None,
            # "created_fire_id": None,
            # "twitter_hashtag": None,
            # "data_source": None,
            # "acres_burned": None,
            # "containment_percent": None,
            # "last_scraped": None,
            # "last_updated": None,
            # "year": None,
            # "date_time_started": None,
            # "administrative_unit": None,
            # "location": None,
            # "location_latitude": None,
            # "location_longitude": None,
            # "location_geocode_error": None,
            # "injuries": None,
            # "evacuations": None,
            # "structures_threatened": None,
            # "structures_destroyed": None,
            # "total_dozers": None,
            # "total_helicopters": None,
            # "total_fire_engines": None,
            # "total_fire_personnel": None,
            # "total_water_tenders": None,
            # "total_airtankers": None,
            # "total_fire_crews": None,
            # "cause": None,
            # "cooperating_agencies": None,
            # "road_closures": None,
            # "school_closures": None,
            # "conditions": None,
            # "current_situation": None,
            # "phone_numbers": None,
            # "more_info": None,
        }


class Normalizer(object):

    def extract_acres(self, string):
        """
        runs regex on acres cell to return acres burned as int
        """
        target_number = string.replace(",", "")
        number_check = re.compile("\d+\sacres")
        extract_acreage = re.compile("\d+\sacres")
        extract_number = re.compile("^\d+")
        match = re.search(number_check, target_number)
        if match:
            try:
                target_number = re.search(extract_acreage, target_number).group()
                target_number = re.search(extract_number, target_number).group()
                target_number = int(target_number)
                return target_number
            except Exception, exception:
                logger.error("%s" % (exception))
                raise
        else:
            match = re.search(extract_number, target_number)
            if match:
                try:
                    target_number = re.search(extract_number, target_number).group()
                    target_number = int(target_number)
                    return target_number
                except Exception, exception:
                    logger.error("%s" % (exception))
                    raise
            else:
                target_number = None
                return target_number


    def extract_containment(self, string):
        """
        runs regex on acres cell to return containment as int
        """
        extract_surrounded_number = re.compile("(\d+)")
        string = string.replace(",", "").replace(" - ", " ").strip()
        sign_match = re.search("%", string)
        percent_match = re.search("percent", string)
        contain_match = re.search("contain", string)
        if sign_match:
            containment = re.findall(extract_surrounded_number, string)
        elif percent_match:
            containment = re.findall(extract_surrounded_number, string)
        elif contain_match:
            containment = re.findall(extract_surrounded_number, string)
        else:
            containment = []
        try:
            if len(containment) == 2:
                target_number = containment[1]
            elif len(containment) == 1:
                target_number = containment[0]
            elif len(containment) == 0:
                target_number = None
            else:
                target_number = None
        except Exception, exception:
            logger.error("%s" % (exception))
            raise
        if target_number:
            target_number = int(target_number)
            return target_number
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


    def split_lat_lng_pairs(self, string):
        """
        splits a latitude/longitude pair and returns a list
        """
        if "/" in string:

            string = string.replace(", ", "")
            outlist = string.split("/")
        else:
            outlist = string.split(",")
        return outlist


    def slugify(self, string):
        """
        take a string and make it a slug
        """
        value = re.sub("[^0-9a-zA-Z\s-]+", " ", string.lower())
        pretty_name = " ".join(value.split())
        slug = pretty_name.encode("ascii", "ignore").lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        slug = re.sub(r"[-]+", "-", slug)
        return slug


    def marshal_fire_data(self, f):
        """
        rigorous attempt to normalize scraped data
        """
        if f.has_key("name"):
            f["name"] = f["name"].replace(":", "")
            if "Fire" in f["name"]:
                f["name"] = f["name"]
            elif "fire" in f["name"]:
                f["name"] = f["name"]
            else:
                f["name"] = "%s Fire" % (f["name"])
            f["twitter_hashtag"] = "#%s" % (f["name"].title().replace(" ", ""))
        else:
            raise

        if f.has_key("county"):
            if f["county"] == "Los Angele":
                f["county"] = "Los Angeles County"
        else:
            f["county"] = None

        if f.has_key("created_fire_id"):
            f["created_fire_id"] = f["created_fire_id"].replace(":", "")
        else:
            f["created_fire_id"] = "%s-%s" % (f["name"], f["county"])

        if f.has_key("acres_burned_containment"):
            f["acres_burned"] = self.extract_acres(f["acres_burned_containment"])
            f["containment_percent"] = self.extract_containment(f["acres_burned_containment"])
        elif f.has_key("containment"):
            f["acres_burned"] = self.extract_acres(f["containment"])
            f["containment_percent"] = self.extract_containment(f["containment"])
        else:
            f["acres_burned"] = None
            f["containment_percent"] = None

        if f.has_key("details_source"):
            f["details_source"] = f["details_source"]
        else:
            f["details_source"] = None

        if f.has_key("date_time_started"):
            f["date_time_started"] = self.convert_time_to_nicey_format(f["date_time_started"])
            f["year"] = f["date_time_started"].year
        elif f.has_key("date_started"):
            f["date_time_started"] = self.convert_time_to_nicey_format(f["date_started"])
            f["year"] = f["date_time_started"].year
        else:
            f["date_time_started"] = None
            f["year"] = None

        if f.has_key("last_updated"):
            f["last_updated"] = self.convert_time_to_nicey_format(f["last_updated"])
        elif f.has_key("last_update"):
            f["last_updated"] = self.convert_time_to_nicey_format(f["last_update"])
        else:
            f["last_updated"] = datetime.datetime.now()

        if f.has_key("administrative_unit"):
            f["administrative_unit"] = f["administrative_unit"]
        else:
            f["administrative_unit"] = None

        if f.has_key("details_link"):
            f["details_link"] = f["details_link"]
        else:
            f["details_link"] = None

        if f.has_key("location"):
            f["location"] = f["location"].title()
        else:
            f["location"] = None

        if f.has_key("long_lat"):
            try:
                loco_list = self.split_lat_lng_pairs(f["long_lat"])
                try:
                    f["location_latitude"] = loco_list[1].replace("latitude", "").strip()
                    f["location_longitude"] = loco_list[0].replace("longitude", "").strip()
                    f["location_geocode_error"] = False
                except:
                    f["location_latitude"] = loco_list[1].strip()
                    f["location_longitude"] = loco_list[0].strip()
                    f["location_geocode_error"] = False
            except:
                f["location_latitude"] = None
                f["location_longitude"] = None
                f["location_geocode_error"] = True
        else:
            f["location_latitude"] = None
            f["location_longitude"] = None
            f["location_geocode_error"] = True

        if f.has_key("injuries"):
            f["injuries"] = self.extract_initial_integer(f["injuries"])
        else:
            f["injuries"] = None

        if f.has_key("evacuations"):
            f["evacuations"] = f["evacuations"]
        else:
            f["evacuations"] = None

        if f.has_key("structures_threatened"):
            f["structures_threatened"] = f["structures_threatened"]
        else:
            f["structures_threatened"] = None

        if f.has_key("structures_destroyed"):
            f["structures_destroyed"] = f["structures_destroyed"]
        else:
            f["structures_destroyed"] = None

        if f.has_key("total_dozers"):
            f["total_dozers"] = self.extract_initial_integer(f["total_dozers"])
        else:
            f["total_dozers"] = None
        if f.has_key("total_helicopters"):
            f["total_helicopters"] = self.extract_initial_integer(f["total_helicopters"])
        else:
            f["total_helicopters"] = None
        if f.has_key("total_fire_engines"):
            f["total_fire_engines"] = self.extract_initial_integer(f["total_fire_engines"])
        else:
            f["total_fire_engines"] = None
        if f.has_key("total_fire_personnel"):
            f["total_fire_personnel"] = self.extract_initial_integer(f["total_fire_personnel"])
        else:
            f["total_fire_personnel"] = None
        if f.has_key("total_water_tenders"):
            f["total_water_tenders"] = self.extract_initial_integer(f["total_water_tenders"])
        else:
            f["total_water_tenders"] = None
        if f.has_key("total_airtankers"):
            f["total_airtankers"] = self.extract_initial_integer(f["total_airtankers"])
        else:
            f["total_airtankers"] = None
        if f.has_key("total_fire_crews"):
            f["total_fire_crews"] = self.extract_initial_integer(f["total_fire_crews"])
        else:
            f["total_fire_crews"] = None

        if f.has_key("cause"):
            f["cause"] = f["cause"]
        else:
            f["cause"] = None

        if f.has_key("cooperating_agencies"):
            f["cooperating_agencies"] = f["cooperating_agencies"]
        else:
            f["cooperating_agencies"] = None

        if f.has_key("road_closures_"):
            f["road_closures_"] = f["road_closures_"]
        else:
            f["road_closures_"] = None

        if f.has_key("school_closures_"):
            f["school_closures_"] = f["school_closures_"]
        else:
            f["school_closures_"] = None

        if f.has_key("conditions"):
            f["conditions"] = f["conditions"]
        else:
            f["conditions"] = None

        if f.has_key("current_situation"):
            f["current_situation"] = f["current_situation"]
        elif f.has_key("remarks"):
            f["current_situation"] = f["remarks"]
        else:
            f["current_situation"] = None

        if f.has_key("phone_numbers"):
            f["phone_numbers"] = f["phone_numbers"]
        else:
            f["phone_numbers"] = None

        f["last_scraped"] = datetime.datetime.now()

        f["county_slug"] = self.slugify(f["county"])

        f["fire_slug"] = self.slugify(f["name"])

        f["naming_slug"] = "%s-%s" % (f["fire_slug"], f["county_slug"])

        return f


class RetrieveCalFireCurrentIncidents(object):
    """
    """

    req = Requester()
    prep = Prepper()
    norm = Normalizer()
    svr = Saver()
    source = WildfireSource.objects.filter(source_short="calfire", source_active=True)[0]

    def _init(self, *args, **kwargs):
        """
        """
        self.source.raw_html = self.req._make_request_to(self.source.source_url)
        self.source.soup = self.req._make_soup_from(self.source.raw_html)
        if self.source.extraction_type == "Simple Scrape":
            self.req._extract_simple_data_from(self.source)
        else:
            logger.debug("**need a new scraper**")
        for table in self.source.target_content:
            f = self.prep.give_fire()
            f["name"] = table.findAll("tr")[0].findAll("td")[0].text.encode("utf-8")
            f["name"] = f["name"].replace(":", "").replace("more info...", "").strip()
            f["details_source"] = self.source.source_short
            table_row = table.findAll("tr")[1:]
            f = self.prep.tablerow_to_dicts(table_row, f)
            f["details_link"] = self.prep.has_calfire_link(table.findAll("tr")[0].findAll("td")[0])
            if f["details_link"]:
                logger.debug("gonna need to request the details url")
                raw_html = self.req._make_request_to(f["details_link"])
                soup = self.req._make_soup_from(raw_html)
                table = soup.findAll("table", {"id": "incident_information"})
                table_row = table[0].findAll("tr")[1:]
                f = self.prep.tablerow_to_dicts(table_row, f)
            f["update_this_fire"] = self.prep.fire_exists_and_is_new(f)
            # f = {k: v for k, v in f.iteritems() if v is not None}
            output = self.norm.marshal_fire_data(f)
            self.svr.save_dict_to_model(output)


if __name__ == "__main__":
    task_run = CompileCalFireResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
