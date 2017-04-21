#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from datetime import tzinfo
from pytz import timezone
from dateutil import parser

logger = logging.getLogger("calfire_tracker")


class Saver(object):
    """
    a series of reusable methods if you
    change something in here you're gonna
    want to change something in the
    test_utils_request script as well
    """

    date_object = datetime.datetime.now()
    date_string = date_object.strftime("%Y_%m_%d_%H_%M_%S")
    log_message = "\n*** Beginning Request ***\n"

    def save_dict_to_model(self, fire):
        """
        save data stored in dict to models
        """
        fires_to_ignore = [
            "Oroville Spillway-Butte County",
            "South Napa Earthquake-Napa County",
            "Reservoir Fire-Los Angeles County",
            "Fish Fire-Los Angeles County",
        ]
        if fire["created_fire_id"] in fires_to_ignore:
            pass
        elif fire["name"] == "Reservoir Fire" and fire["date_time_started"] == "June 20, 2016 1:59 pm":
            pass
        elif fire["name"] == "Fish Fire" and fire["date_time_started"] == "June 20, 2016 11:20 am":
            pass
        elif fire["name"] == "Shirley Fire" and fire["last_updated"] == "June 20, 2014 8:30 am":
            fire["details_source"] = "Inciweb"
            fire["details_link"] = "http://inciweb.nwcg.gov/incident/3895/"
        elif fire["name"] == "Butte Fire" and fire["details_link"] == "http://cdfdata.fire.ca.gov/incidents/incidents_details_info?incident_id=1221":
            fire["created_fire_id"] = "Butte Fire-Amador & Calaveras Counties"
            fire["details_link"] = "http://cdfdata.fire.ca.gov/incidents/incidents_details_info?incident_id=1221"
            fire["county"] = "Amador County & Calaveras County"
        elif fire["name"] == "Valley Fire" and fire["details_link"] == "http://cdfdata.fire.ca.gov/incidents/incidents_details_info?incident_id=1226":
            fire["created_fire_id"] = "Valley Fire-Lake, Napa and Sonoma Counties"
            details_link = fire["details_link"]
        elif fire["name"] == "Mason Fire" and fire["details_link"] == "http://inciweb.nwcg.gov/incident/4382/":
            fire["details_source"] = "Inciweb"
            fire["details_link"] = "http://inciweb.nwcg.gov/incident/4275/"
        elif fire["name"] == "Gasquet Complex":
            fire["details_source"] = "Inciweb"
            fire["details_link"] = "http://inciweb.nwcg.gov/incident/4444/"
        elif fire["name"] == "Mad River Complex":
            fire["details_source"] = "Inciweb"
            fire["details_link"] = "http://inciweb.nwcg.gov/incident/4436/"
        else:
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

                # elif created:
                #     if SCRAPER_VARIABLES["status"] == "live":
                #         self.UTIL.send_new_fire_email(
                #             fire["name"],
                #             fire["acres_burned"],
                #             fire["county"],
                #             fire["containment_percent"]
                #         )

                else:
                    try:
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
                        # obj.location_latitude = fire["location_latitude"]
                        # obj.location_longitude = fire["location_longitude"]
                        # obj.location_geocode_error = fire["location_geocode_error"]
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
