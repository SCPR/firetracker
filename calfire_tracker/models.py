from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from geopy import geocoders
import pytz
import time, datetime

class CalWildfire(models.Model):

    # management & curation
    created_fire_id = models.CharField('Fire Unique ID', max_length=500, null=True, blank=True)
    promoted_fire = models.BooleanField('Feature This Fire?', default=False)
    asset_host_image_id = models.CharField('Image ID from Asset Host', max_length=140, null=True, blank=True)
    twitter_hashtag = models.CharField('Twitter Hashtag', max_length=140, null=True, blank=True)
    air_quality_rating = models.IntegerField('Air Quality Rating from http://airnow.gov/', max_length=3, null=True, blank=True)
    last_scraped = models.DateTimeField('Last Scraped', null=True, blank=True)

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

    # location information
    location = models.TextField('Location from Cal Fire ', null=True, blank=True)
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

    def save(self, *args, **kwargs):
        #if not self.id:
            #self.fire_slug = slugify(self.fire_name)
        if not self.created_fire_id:
        	self.created_fire_id = self.created_fire_id
        if (self.location_latitude is None) or (self.location_longitude is None):
            self.fill_geocode_data()
        super(CalWildfire, self).save()

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