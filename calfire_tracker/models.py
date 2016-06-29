from django.conf import settings
from django.contrib import messages
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from geopy import geocoders
import pytz
import time
import datetime
import requests
import logging
from utilities import *

logger = logging.getLogger("firetracker")


class CalWildfire(models.Model):

    # management & curation
    created_fire_id = models.CharField("Fire Unique ID", max_length=500, null=True, blank=True, help_text="We use this to see if a given fire already exists")
    update_lockout = models.BooleanField("Lock Data?", default=False)
    fire_closeout_toggle = models.BooleanField("Close This Fire?", default=False)
    promoted_fire = models.BooleanField("Feature This?", default=False)
    asset_host_image_id = models.CharField("Asset Host Image ID", max_length=140, null=True, blank=True)
    asset_url_link = models.URLField("Image Source URL", max_length=1024, null=True, blank=True)
    asset_photo_credit = models.CharField("Image Credit", max_length=1024, null=True, blank=True)
    twitter_hashtag = models.CharField("Twitter Hashtag", max_length=140, null=True, blank=True)
    air_quality_rating = models.IntegerField("Air Quality Rating from http://airnow.gov/", max_length=3, null=True, blank=True)
    air_quality_parameter = models.CharField("Air Quality Description - Fine particles (PM2.5) or Ozone (O3)", max_length=200, null=True, blank=True)
    last_scraped = models.DateTimeField("Last Scraped", null=True, blank=True)
    last_saved = models.DateTimeField("Last Saved", auto_now=True)
    data_source = models.CharField("Data Source", max_length=1024, null=True, blank=True, help_text="CalFire, Inciweb, etc.")

    # general details
    fire_name = models.CharField("Fire Name", max_length=1024, null=True, blank=True)
    county = models.CharField("County Name", max_length=1024, null=True, blank=True)
    acres_burned = models.IntegerField("Acres Burned", max_length=8, null=True, blank=True)
    containment_percent = models.IntegerField("Percent Contained", max_length=4, null=True, blank=True)
    date_time_started = models.DateTimeField("Date Fire Started", null=True, blank=True)
    last_updated = models.DateTimeField("Information As Of", null=True, blank=True)
    administrative_unit = models.CharField("Administrative Unit", max_length=1024, null=True, blank=True, help_text="Agency overseeing the firefighting efforts")
    more_info = models.URLField("URL To More Info", max_length=1024, null=True, blank=True)
    fire_slug = models.SlugField("Fire Slug", max_length=140, null=True, blank=True, help_text="URL this fire will appear at")
    county_slug = models.SlugField("County Slug", max_length=140, null=True, blank=True, help_text="County name as a slug for searching purposes.")
    year = models.IntegerField("Fire Year", max_length=4, null=True, blank=True, help_text="We use this to categorize when the fire occured")

    # location information
    location = models.TextField("Location text displayed to public", null=True, blank=True)
    computed_location = models.TextField("Location we'll try to geocode", null=True, blank=True)
    location_latitude = models.FloatField("Latitude Coords", null=True, blank=True)
    location_longitude = models.FloatField("Longitude Coords", null=True, blank=True)
    location_geocode_error = models.BooleanField("Is missing geocoded coordinates", default=True)
    perimeters_image = models.URLField("Url to Perimeter Image", max_length=1024, null=True, blank=True)

    # fire stats
    injuries = models.CharField("Reported Injuries", max_length=2024, null=True, blank=True)
    evacuations = models.TextField("Reported Evacuations", null=True, blank=True)
    structures_threatened = models.CharField("Structures Threatened", max_length=1024, null=True, blank=True)
    structures_destroyed = models.CharField("Structures Destroyed", max_length=1024, null=True, blank=True)

    # resources deployed
    total_dozers = models.IntegerField("Dozers Deployed", max_length=10, null=True, blank=True)
    total_helicopters = models.IntegerField("Helicopters Deployed", max_length=10, null=True, blank=True)
    total_fire_engines = models.IntegerField("Fire Engines Deployed", max_length=10, null=True, blank=True)
    total_fire_personnel = models.IntegerField("Fire Personnel Deployed", max_length=10, null=True, blank=True)
    total_water_tenders = models.IntegerField("Water Tenders Deployed", max_length=10, null=True, blank=True)
    total_airtankers = models.IntegerField("Airtankers Deployed", max_length=10, null=True, blank=True)
    total_fire_crews = models.IntegerField("Fire Crews Deployed", max_length=10, null=True, blank=True)

    # situation on the ground
    cause = models.TextField("Cause", null=True, blank=True)
    cooperating_agencies = models.TextField("Cooperating Agencies", null=True, blank=True)
    road_closures = models.TextField("Road Closures", null=True, blank=True)
    school_closures = models.TextField("School Closures", null=True, blank=True)
    conditions = models.TextField("Conditions", null=True, blank=True)
    current_situation = models.TextField("Current Situation", null=True, blank=True)
    damage_assessment = models.TextField("Damage Assessment", null=True, blank=True)
    training = models.TextField("Training", null=True, blank=True)
    phone_numbers = models.TextField("Phone Numbers", null=True, blank=True)
    notes = models.TextField("Passoff Notes/Contact Information", null=True, blank=True)
    historical_narrative = models.TextField("Historical Narrative", null=True, blank=True)

    class Meta:
        app_label = 'calfire_tracker'

    def __unicode__(self):
        return self.fire_name

    @models.permalink
    def get_absolute_url(self):
        return ("detail", [self.fire_slug, ])

    def save(self, *args, **kwargs):

        now = datetime.datetime.now()

        self.last_saved = datetime.datetime.now()

        if not self.year:
            if self.date_time_started:
                self.year = self.date_time_started.year
            else:
                self.year = datetime.date.today().year

        if not self.created_fire_id:
            try:
                self.created_fire_id = "%s-%s-%s" % (self.fire_name, self.county, self.year)
            except Exception, exception:
                logger.error(exception)

        # if self.pk is None and not self.fire_slug:
            # self.fire_slug = "%s-%s-%s" % (slugify(self.fire_name), slugify(self.county), self.year)
        # elif not self.contestid:
            # self.fire_slug = "%s-%s-%s" % (slugify(self.fire_name), slugify(self.county), self.year)

        if not self.fire_slug:
            self.fire_slug = "%s-%s-%s" % (slugify(self.fire_name), slugify(self.county), self.year)

        if not self.county_slug:
            try:
                self.county_slug = slugify(self.county)
            except Exception, exception:
                logger.error(exception)
                raise

        if not self.acres_burned:
            logger.debug("need self.acres_burned")

        if not self.date_time_started:
            logger.debug("need self.date_time_started")

        if not self.twitter_hashtag:
            try:
                self.twitter_hashtag = "#%s" % (self.fire_name.replace(" ", ""))
            except Exception, exception:
                logger.error(exception)
                logger.debug("need self.twitter_hashtag")

        # geocoding functions
        if (self.location_latitude is None) or (self.location_longitude is None):
            if self.computed_location:
                try:
                    geolocation_data = fill_geocode_data(
                        self.computed_location)
                    self.computed_location = geolocation_data[
                        "computed_location"]
                    self.location_latitude = geolocation_data[
                        "location_latitude"]
                    self.location_longitude = geolocation_data[
                        "location_longitude"]
                    self.location_geocode_error = geolocation_data[
                        "location_geocode_error"]
                except:
                    self.computed_location = None
                    self.location_geocode_error = True
            else:
                self.location_geocode_error = True

        if self.air_quality_rating == None:
            if (self.location_latitude != None) or (self.location_longitude != None):
                air_quality_data = fill_air_quality_data(
                    self.location_latitude, self.location_longitude)
                self.air_quality_rating = air_quality_data[
                    "air_quality_rating"]
                self.air_quality_parameter = air_quality_data[
                    "air_quality_parameter"]
        elif self.air_quality_rating != None:
            current_air_quality_rating = self.air_quality_rating
            current_air_quality_parameter = self.air_quality_parameter
            if (self.location_latitude != None) or (self.location_longitude != None):
                air_quality_data = fill_air_quality_data(
                    self.location_latitude, self.location_longitude)
                if air_quality_data["air_quality_rating"] == None:
                    self.air_quality_rating = current_air_quality_rating
                    self.air_quality_parameter = current_air_quality_parameter
                else:
                    self.air_quality_rating = air_quality_data[
                        "air_quality_rating"]
                    self.air_quality_parameter = air_quality_data[
                        "air_quality_parameter"]

        # query for asset host image
        if not self.asset_host_image_id:
            if not self.asset_url_link:
                pass
            else:
                asset_url_link = self.asset_url_link.replace(
                    "&width=1024&source=firetracker", "")
                self.asset_url_link = "%s&width=1024&source=firetracker" % (
                    asset_url_link)
        else:
            asset_host_image_id = self.asset_host_image_id
            kpcc_image_data = search_assethost_for_image(
                settings.ASSETHOST_TOKEN_SECRET, image_id=asset_host_image_id)
            self.asset_host_image_id = kpcc_image_data["asset_host_image_id"]
            self.asset_url_link = kpcc_image_data["asset_url_link"]
            self.asset_photo_credit = kpcc_image_data["asset_photo_credit"]

        # run the save function
        super(CalWildfire, self).save(*args, **kwargs)


class AltCreateWildfire(CalWildfire):
    class Meta:
        proxy = True
        app_label = 'calfire_tracker'
        verbose_name = 'AltCreateWildfire'
        verbose_name_plural = 'Beta Create/Edit Wildfires'


class WildfireUpdate(models.Model):
    date_time_update = models.DateTimeField("Time of Update", null=True, blank=True)
    fire_name = models.ForeignKey(CalWildfire, null=True, blank=True, related_name="calwildfire_fire_name")
    update_text = models.TextField("Latest Update", null=True, blank=True)
    source = models.URLField("Source", max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.update_text

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_time_update = datetime.datetime.now()
        super(WildfireUpdate, self).save()


class WildfireTweet(models.Model):
    tweet_hashtag = models.CharField("Tweet Hashtag", max_length=1024, null=True, blank=True)
    tweet_text = models.TextField("Tweet Text", null=True, blank=True)
    tweet_created_at = models.DateTimeField("Tweet Date/Time", null=True, blank=True)
    tweet_id = models.CharField("Tweet ID", max_length=1024, null=True, blank=True)
    tweet_screen_name = models.CharField("Tweet User", max_length=1024, null=True, blank=True)
    tweet_profile_image_url = models.URLField("Tweet Profile Image", max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.tweet_screen_name

    def save(self, *args, **kwargs):
        if not self.tweet_id:
            self.tweet_id = self.tweet_id
        super(WildfireTweet, self).save()


class WildfireAnnualReview(models.Model):
    year = models.IntegerField("Fire Year", max_length=4, null=True, blank=True)
    date_range_beginning = models.DateTimeField("Beginning Date Range", null=False)
    date_range_end = models.DateTimeField("Ending Date Range", null=False)
    acres_burned = models.IntegerField("Acres Burned", max_length=8, null=True, blank=True)
    number_of_fires = models.IntegerField("Number of Fires", max_length=10, null=True, blank=True)
    dollar_damage = models.DecimalField("Dollar Damage", max_digits=15, decimal_places=2, null=True, blank=True)
    injuries = models.CharField("Reported Injuries", max_length=2024, null=True, blank=True)
    structures_threatened = models.CharField("Reported Structures Threatened", max_length=1024, null=True, blank=True)
    structures_destroyed = models.CharField("Reported Structures Destroyed", max_length=1024, null=True, blank=True)
    administrative_unit = models.CharField("Administrative Unit", max_length=1024, null=True, blank=True)
    jurisdiction = models.CharField("Jurisdiction", max_length=1024, null=True, blank=True)
    data_source = models.URLField("URL to data source", max_length=1024, null=True, blank=True)
    last_saved = models.DateTimeField("Last Saved", auto_now=True)

    def __unicode__(self):
        return self.jurisdiction

    def save(self, *args, **kwargs):
        if not self.id:
            self.last_saved = datetime.datetime.now()
        super(WildfireAnnualReview, self).save()


class WildfireDisplayContent(models.Model):

    """
    content_type_choices = (
        ("Resource Content", "Resource Content"),
        ("Display Content", "Display Content"),
    )
    content_type = models.MultipleChoiceField(null=True, choices=content_type_choices, default=content_type_choices[0][0])
    """

    resource_content_type = models.BooleanField("Resource Content", default=True)
    display_content_type = models.BooleanField("Display Content", default=False)
    content_headline = models.TextField("Display Text", null=True, blank=True)
    content_link = models.URLField("Display Link", max_length=1024, null=True, blank=True)
    last_saved = models.DateTimeField("Last Saved", auto_now=True)

    def __unicode__(self):
        return self.content_headline
