from datetime import datetime, date, time, timedelta
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext
from django.db.models import Q, Avg, Max, Min, Sum, Count
from django.utils import simplejson
from calfire_tracker.models import CalWildfire, WildfireUpdate, WildfireTweet
from django.conf import settings
from dateutil import parser
from kpccapi import *
import logging

logging.basicConfig(level=logging.DEBUG)

@xframe_options_sameorigin
def index(request):

    wildfires = CalWildfire.objects.all()
    calwildfires = wildfires.exclude(containment_percent=None).order_by('containment_percent', '-date_time_started', 'fire_name')[0:20]
    featuredfires = wildfires.filter(promoted_fire=True).order_by('containment_percent', '-date_time_started', 'fire_name')[0:3]
    cache_timestamp = wildfires.all().order_by('-last_saved')

    total_2013_fires = 4715
    total_2013_acreage = 94855
    total_2013_injuries = None

    total_2012_fires = 5809
    total_2012_acreage = 141154
    total_2012_injuries = None

    cache_expire = (60*60*24)
    cache_timestamp = cache_timestamp[0].last_saved

    return render_to_response('index.html', {
        'calwildfires': calwildfires,
        'featuredfires': featuredfires,
        'total_2013_fires': total_2013_fires,
        'total_2013_acreage': total_2013_acreage,
        'total_2013_injuries': total_2013_injuries,
        'total_2012_fires': total_2012_fires,
        'total_2012_acreage': total_2012_acreage,
        'total_2012_injuries': total_2012_injuries,
        'cache_expire': cache_expire,
        'cache_timestamp': cache_timestamp
    })

@xframe_options_sameorigin
def detail(request, fire_slug):
    calwildfire = get_object_or_404(CalWildfire, fire_slug=fire_slug)
    calwildfires = CalWildfire.objects.exclude(containment_percent=None).order_by('containment_percent', '-date_time_started', 'fire_name')[0:15]
    wildfire_updates = WildfireUpdate.objects.filter(fire_name__fire_name=calwildfire.fire_name).order_by('-date_time_update')
    result_list = WildfireTweet.objects.filter(tweet_hashtag=calwildfire.twitter_hashtag).order_by('-tweet_created_at')

    cache_expire = (60*60*24)

    return render_to_response('detail.html', {
        'calwildfire': calwildfire,
        'calwildfires': calwildfires,
        'wildfire_updates': wildfire_updates,
        'result_list': result_list,
        'cache_expire': cache_expire,
    }, context_instance=RequestContext(request))

@xframe_options_exempt
def embeddable(request, fire_slug):
    calwildfire = get_object_or_404(CalWildfire, fire_slug=fire_slug)

    cache_expire = (60*60*24)

    return render_to_response('embeddable.html', {
        'calwildfire': calwildfire,
        'cache_expire': cache_expire,
    }, context_instance=RequestContext(request))

@xframe_options_sameorigin
def archives(request):
    current_year = date.today().year
    calwildfires = CalWildfire.objects.filter(date_time_started__year=current_year).order_by('-date_time_started', 'fire_name')

    cache_expire = (60*60*24)

    return render_to_response('archives.html', {
        'calwildfires': calwildfires,
        'cache_expire': cache_expire,
    })