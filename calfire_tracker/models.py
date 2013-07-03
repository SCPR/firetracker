from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
import pytz
import time, datetime

# Create your models here.
class CalWildfire(models.Model):
    created_fire_id = models.CharField('Fire Unique ID', max_length=500, null=True, blank=True)
    fire_slug = models.SlugField('Fire Slug', max_length=140, null=True, blank=True)
    twitter_hashtag = models.CharField('Twitter Hashtag', max_length=140, null=True, blank=True)
    promoted_fire = models.BooleanField(default=False)
    fire_name = models.CharField('Fire Name', max_length=1024, null=True, blank=True)
    county = models.CharField('County', max_length=1024, null=True, blank=True)
    location = models.CharField('Location', max_length=1024, null=True, blank=True)
    location_latitude = models.FloatField('Latitude', null=True, blank=True)
    location_longitude = models.FloatField('Longitude', null=True, blank=True)
    location_geocode_error = models.BooleanField(default=False)
    administrative_unit = models.CharField('Administrative Unit', max_length=1024, null=True, blank=True)
    more_info = models.URLField('More Info', max_length=1024, null=True, blank=True)
    acres_burned = models.IntegerField('Acres Burned', max_length=8, null=True, blank=True)
    containment_percent = models.IntegerField('Containment Percent', max_length=4, null=True, blank=True)
    last_updated = models.DateTimeField('Last Update', null=True, blank=True)
    date_time_started = models.DateTimeField('Date Started', null=True, blank=True)
    phone_numbers = models.TextField('Phone Numbers', max_length=1024, null=True, blank=True)
    evacuations = models.TextField('Evacuations', max_length=1024, null=True, blank=True)
    structures_threatened = models.CharField('Structures Threatened', max_length=1024, null=True, blank=True)
    injuries = models.CharField('Injuries', max_length=1024, null=True, blank=True)
    road_closures = models.TextField('Road Closures', max_length=1024, null=True, blank=True)
    structures_destroyed = models.CharField('Structures Destroyed', max_length=1024, null=True, blank=True)
    total_dozers = models.IntegerField('Total Dozers', max_length=10, null=True, blank=True)
    total_helicopters = models.IntegerField('Total Helicopters', max_length=10, null=True, blank=True)
    total_fire_engines = models.IntegerField('Total Fire Engines', max_length=10, null=True, blank=True)
    total_fire_personnel = models.IntegerField('Total Fire Personnel', max_length=10, null=True, blank=True)
    total_water_tenders = models.IntegerField('Total Water Tenders', max_length=10, null=True, blank=True)
    cause = models.TextField('Cause', max_length=1024, null=True, blank=True)
    total_airtankers = models.IntegerField('Total Airtankers', max_length=10, null=True, blank=True)
    conditions = models.TextField('Conditions', null=True, blank=True)
    cooperating_agencies = models.TextField('Cooperating Agencies', max_length=1024, null=True, blank=True)
    total_fire_crews = models.IntegerField('Total Fire Crews', max_length=10, null=True, blank=True)
    notes = models.TextField('Notes', max_length=1024, null=True, blank=True)
    last_scraped = models.DateTimeField('Last Scraped', null=True, blank=True)

    def __unicode__(self):
        return self.fire_name

    @models.permalink
    def get_absolute_url(self):
        return ('detail', [self.fire_slug,])

    def save(self, *args, **kwargs):
        #if not self.id:
            #self.fire_slug = slugify(self.fire_name)
        if not self.created_fire_id:
        	self.created_fire_id = self.created_fire_id
        super(CalWildfire, self).save()