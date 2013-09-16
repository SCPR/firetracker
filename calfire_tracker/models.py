from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from geopy import geocoders
import pytz
import time, datetime
import simplejson as json
import urllib
import logging

logging.basicConfig(level=logging.DEBUG)

class CalWildfire(models.Model):

    # management & curation
    created_fire_id = models.CharField('Fire Unique ID', max_length=500, null=True, blank=True)
    update_lockout = models.BooleanField('Lock Data?', default=False)
    promoted_fire = models.BooleanField('Feature This?', default=False)
    asset_host_image_id = models.CharField('Asset Host Image ID', max_length=140, null=True, blank=True)
    asset_url_link = models.URLField('Image Source URL', max_length=1024, null=True, blank=True)
    asset_photo_credit = models.CharField('Image Credit', max_length=1024, null=True, blank=True)
    twitter_hashtag = models.CharField('Twitter Hashtag', max_length=140, null=True, blank=True)
    air_quality_rating = models.IntegerField('Air Quality Rating from http://airnow.gov/', max_length=3, null=True, blank=True)
    last_scraped = models.DateTimeField('Last Scraped', null=True, blank=True)
    last_saved = models.DateTimeField('Last Saved', auto_now=True)
    data_source = models.CharField('Data Source', max_length=1024, null=True, blank=True)

    # general details
    fire_name = models.CharField('Fire Name', max_length=1024, null=True, blank=True)
    county = models.CharField('County Name', max_length=1024, null=True, blank=True)
    acres_burned = models.IntegerField('Acres Burned', max_length=8, null=True, blank=True)
    containment_percent = models.IntegerField('Percent Contained', max_length=4, null=True, blank=True)
    date_time_started = models.DateTimeField('Date Fire Started', null=True, blank=True)
    last_updated = models.DateTimeField('Last Fire Update', null=True, blank=True)
    administrative_unit = models.CharField('Administrative Unit', max_length=1024, null=True, blank=True)
    more_info = models.URLField('URL To More Info', max_length=1024, null=True, blank=True)
    fire_slug = models.SlugField('Fire Slug', max_length=140, null=True, blank=True)
    county_slug = models.SlugField('County Slug', max_length=140, null=True, blank=True)
    year = models.IntegerField('Fire Year', max_length=4, null=True, blank=True)

    # location information
    location = models.TextField('Location from Cal Fire', null=True, blank=True)
    computed_location = models.TextField('Location to Geocode', null=True, blank=True)
    location_latitude = models.FloatField('Geocoded Latitude', null=True, blank=True)
    location_longitude = models.FloatField('Geocoded Longitude', null=True, blank=True)
    location_geocode_error = models.BooleanField('Needs Geocoded Location', default=True)

    # fire stats
    injuries = models.CharField('Reported Injuries', max_length=2024, null=True, blank=True)
    evacuations = models.TextField('Reported Evacuations', null=True, blank=True)
    structures_threatened = models.CharField('Reported Structures Threatened', max_length=1024, null=True, blank=True)
    structures_destroyed = models.CharField('Reported Structures Destroyed', max_length=1024, null=True, blank=True)

    # resources deployed
    total_dozers = models.IntegerField('Dozers Deployed', max_length=10, null=True, blank=True)
    total_helicopters = models.IntegerField('Helicopters Deployed', max_length=10, null=True, blank=True)
    total_fire_engines = models.IntegerField('Fire Engines Deployed', max_length=10, null=True, blank=True)
    total_fire_personnel = models.IntegerField('Fire Personnel Deployed', max_length=10, null=True, blank=True)
    total_water_tenders = models.IntegerField('Water Tenders Deployed', max_length=10, null=True, blank=True)
    total_airtankers = models.IntegerField('Airtankers Deployed', max_length=10, null=True, blank=True)
    total_fire_crews = models.IntegerField('Fire Crews Deployed', max_length=10, null=True, blank=True)

    # situation on the ground
    cause = models.TextField('Cause', null=True, blank=True)
    cooperating_agencies = models.TextField('Cooperating Agencies', null=True, blank=True)
    road_closures = models.TextField('Road Closures', null=True, blank=True)
    school_closures = models.TextField('School Closures', null=True, blank=True)
    conditions = models.TextField('Conditions', null=True, blank=True)
    current_situation = models.TextField('Current Situation', null=True, blank=True)
    damage_assessment = models.TextField('Damage Assessment', null=True, blank=True)
    training = models.TextField('Training', null=True, blank=True)
    phone_numbers = models.TextField('Phone Numbers', null=True, blank=True)
    notes = models.TextField('Notes', null=True, blank=True)

    def __unicode__(self):
        return self.fire_name

    @models.permalink
    def get_absolute_url(self):
        return ('detail', [self.fire_slug,])

    def fill_geocode_data(self):
        if not self.computed_location:
            self.location_geocode_error = True
        else:
            try:
                g = geocoders.GoogleV3()
                address = smart_str(self.computed_location)
                self.computed_location, (self.location_latitude, self.location_longitude,) = g.geocode(address)
                self.location_geocode_error = False
            except (UnboundLocalError, ValueError,geocoders.google.GQueryError):
                self.location_geocode_error = True

    def search_assethost_for_image(self, kpcc_image_token):
        url_prefix = 'http://a.scpr.org/api/assets/'
        url_suffix = '.json?auth_token='
        search_url = '%s%s%s%s' % (url_prefix, self.asset_host_image_id, url_suffix, kpcc_image_token)
        json_response = urllib.urlopen(search_url)
        json_response = json_response.readlines()
        js_object = json.loads(json_response[0])
        try:
            self.asset_url_link = js_object['urls']['full']
            self.asset_photo_credit = js_object['owner']
        except:
            self.asset_host_image_id = 'Could Not Find That ID'
            self.asset_url_link = None
            self.asset_photo_credit = None

    def save(self, *args, **kwargs):
        #if not self.id:
            #self.fire_slug = slugify(self.fire_name)
        if not self.created_fire_id:
        	self.created_fire_id = self.created_fire_id
        if (self.location_latitude is None) or (self.location_longitude is None):
            self.fill_geocode_data()
        if self.asset_host_image_id:
            self.search_assethost_for_image(settings.ASSETHOST_TOKEN_SECRET)
        if not self.asset_host_image_id:
            self.asset_url_link = None
            self.asset_photo_credit = None
        super(CalWildfire, self).save(*args, **kwargs)

class WildfireUpdate(models.Model):
    date_time_update = models.DateTimeField('Time of Update', null=True, blank=True)
    fire_name = models.ForeignKey(CalWildfire, null=True, blank=True, related_name='calwildfire_fire_name')
    update_text = models.TextField('Latest Update', null=True, blank=True)
    source = models.URLField('Source', max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.update_text

    def save(self, *args, **kwargs):
        if not self.id:
        	self.date_time_update = datetime.datetime.now()
        super(WildfireUpdate, self).save()

class WildfireTweet(models.Model):
    tweet_hashtag = models.CharField('Tweet Hashtag', max_length=1024, null=True, blank=True)
    tweet_text = models.TextField('Tweet Text', null=True, blank=True)
    tweet_created_at = models.DateTimeField('Tweet Date/Time', null=True, blank=True)
    tweet_id = models.CharField('Tweet ID', max_length=1024, null=True, blank=True)
    tweet_screen_name = models.CharField('Tweet User', max_length=1024, null=True, blank=True)
    tweet_profile_image_url = models.URLField('Tweet Profile Image', max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.tweet_screen_name

    def save(self, *args, **kwargs):
        if not self.tweet_id:
        	self.tweet_id = self.tweet_id
        super(WildfireTweet, self).save()
