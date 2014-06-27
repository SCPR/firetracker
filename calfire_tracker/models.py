from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from geopy import geocoders
import pytz, time, datetime, requests, logging
from utilities import *

logging.basicConfig(format="\033[1;36m%(levelname)s:\033[0;37m %(message)s", level=logging.DEBUG)

class CalWildfire(models.Model):

    # management & curation
    created_fire_id = models.CharField("Fire Unique ID", max_length=500, null=True, blank=True)
    update_lockout = models.BooleanField("Lock Data?", default=False)
    fire_closeout_toggle = models.NullBooleanField("Close This Fire?", null=True, default=False)
    promoted_fire = models.BooleanField("Feature This?", default=False)
    asset_host_image_id = models.CharField("Asset Host Image ID", max_length=140, null=True, blank=True)
    asset_url_link = models.URLField("Image Source URL", max_length=1024, null=True, blank=True)
    asset_photo_credit = models.CharField("Image Credit", max_length=1024, null=True, blank=True)
    twitter_hashtag = models.CharField("Twitter Hashtag", max_length=140, null=True, blank=True)
    air_quality_rating = models.IntegerField("Air Quality Rating from http://airnow.gov/", max_length=3, null=True, blank=True)
    last_scraped = models.DateTimeField("Last Scraped", null=True, blank=True)
    last_saved = models.DateTimeField("Last Saved", auto_now=True)
    data_source = models.CharField("Data Source", max_length=1024, null=True, blank=True)

    # general details
    fire_name = models.CharField("Fire Name", max_length=1024, null=True, blank=True)
    county = models.CharField("County Name", max_length=1024, null=True, blank=True)
    acres_burned = models.IntegerField("Acres Burned", max_length=8, null=True, blank=True)
    containment_percent = models.IntegerField("Percent Contained", max_length=4, null=True, blank=True)
    date_time_started = models.DateTimeField("Date Fire Started", null=True, blank=True)
    last_updated = models.DateTimeField("Last Fire Update", null=True, blank=True)
    administrative_unit = models.CharField("Administrative Unit", max_length=1024, null=True, blank=True)
    more_info = models.URLField("URL To More Info", max_length=1024, null=True, blank=True)
    fire_slug = models.SlugField("Fire Slug", max_length=140, null=True, blank=True)
    county_slug = models.SlugField("County Slug", max_length=140, null=True, blank=True)
    year = models.IntegerField("Fire Year", max_length=4, null=True, blank=True)

    # location information
    location = models.TextField("Location from Cal Fire", null=True, blank=True)
    computed_location = models.TextField("Location to Geocode", null=True, blank=True)
    location_latitude = models.FloatField("Geocoded Latitude", null=True, blank=True)
    location_longitude = models.FloatField("Geocoded Longitude", null=True, blank=True)
    location_geocode_error = models.BooleanField("Needs Geocoded Location", default=True)
    perimeters_image = models.URLField("Url to Perimeter Image", max_length=1024, null=True, blank=True)

    # fire stats
    injuries = models.CharField("Reported Injuries", max_length=2024, null=True, blank=True)
    evacuations = models.TextField("Reported Evacuations", null=True, blank=True)
    structures_threatened = models.CharField("Reported Structures Threatened", max_length=1024, null=True, blank=True)
    structures_destroyed = models.CharField("Reported Structures Destroyed", max_length=1024, null=True, blank=True)

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
    notes = models.TextField("Notes", null=True, blank=True)
    historical_narrative = models.TextField("Historical Narrative", null=True, blank=True)

    def __unicode__(self):
        return self.fire_name

    @models.permalink
    def get_absolute_url(self):
        return ("detail", [self.fire_slug,])

    def save(self, *args, **kwargs):
        self.last_updated = datetime.datetime.now()
        if not self.created_fire_id:
            self.created_fire_id = "%s-%s" % (self.fire_name, self.county)
        if not self.county_slug:
            try:
                self.county_slug = self.county.replace(" ", "-").lower()
            except:
                pass
        if not self.fire_slug:
            try:
                self.fire_slug = self.created_fire_id.replace(" ", "-").lower()
            except:
                pass
        if not self.twitter_hashtag:
            try:
            	self.twitter_hashtag = "#%s" % (self.fire_name.replace(" ", ""))
            except:
                pass
        if not self.year:
            try:
                self.year = self.date_time_started.year
            except:
                self.year = datetime.date.today().year

        # geocoding functions
        if (self.location_latitude is None) or (self.location_longitude is None):
            if self.computed_location:
                try:
                    geolocation_data = fill_geocode_data(self.computed_location)
                    self.computed_location = geolocation_data["computed_location"]
                    self.location_latitude = geolocation_data["location_latitude"]
                    self.location_longitude = geolocation_data["location_longitude"]
                    self.location_geocode_error = geolocation_data["location_geocode_error"]
                except:
                    self.computed_location = None
                    self.location_geocode_error = True
            else:
                self.location_geocode_error = True

        # query for asset host image
        if not self.asset_host_image_id:
            asset_host_image_id = None
        else:
            asset_host_image_id = self.asset_host_image_id
        kpcc_image_data = search_assethost_for_image(settings.ASSETHOST_TOKEN_SECRET, image_id = asset_host_image_id)
        self.asset_host_image_id = kpcc_image_data["asset_host_image_id"]
        self.asset_url_link = kpcc_image_data["asset_url_link"]
        self.asset_photo_credit = kpcc_image_data["asset_photo_credit"]

        # populate air quality rating from api
        if self.location_geocode_error == True:
            pass
        elif (self.location_latitude is None) or (self.location_longitude is None):
            pass
        elif (self.air_quality_rating is not None):
            pass
        else:
            self.air_quality_rating = fill_air_quality_data(self.location_latitude, self.location_longitude)

        # run the save function
        super(CalWildfire, self).save(*args, **kwargs)

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

    '''
    content_type_choices = (
        ("Resource Content", "Resource Content"),
        ("Display Content", "Display Content"),
    )
    content_type = models.MultipleChoiceField(null=True, choices=content_type_choices, default=content_type_choices[0][0])
    '''

    resource_content_type = models.BooleanField("Resource Content", default=True)
    display_content_type = models.BooleanField("Display Content", default=False)
    content_headline = models.TextField("Display Text", null=True, blank=True)
    content_link = models.URLField("Display Link", max_length=1024, null=True, blank=True)
    last_saved = models.DateTimeField("Last Saved", auto_now=True)

    def __unicode__(self):
        return self.content_headline