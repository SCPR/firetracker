from datetime import datetime, date, time, timedelta
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext
from django.db.models import Q, Avg, Max, Min, Sum, Count
from django.utils import simplejson
from calfire_tracker.models import CalWildfire, WildfireUpdate
from django.conf import settings
import tweepy
from kpccapi import *

def index(request):
    startdate = date.today()
    enddate = timedelta(days=60)
    displaydate = startdate - enddate
    #calwildfires = CalWildfire.objects.all().order_by('-date_time_started', 'fire_name')
    calwildfires = CalWildfire.objects.filter(date_time_started__gte=displaydate).order_by('-date_time_started', 'fire_name')
    so_cal_counties = CalWildfire.objects.filter(Q(county='Los Angeles County') | Q(county='Orange County') | Q(county='Riverside County') | Q(county='San Bernardino County') | Q(county='Ventura County'))
    so_cal_fires = so_cal_counties.filter(date_time_started__year='2013').count()
    so_cal_acreage = so_cal_counties.filter(date_time_started__year='2013').aggregate(total_acres=Sum('acres_burned'))
    total_2013_fires = CalWildfire.objects.filter(date_time_started__year='2013').count()
    total_2013_acreage = CalWildfire.objects.filter(date_time_started__year='2013').aggregate(total_acres=Sum('acres_burned'))
    total_2013_injuries = CalWildfire.objects.filter(date_time_started__year='2013').aggregate(total_injuries=Sum('injuries'))

    #total_2012_fires = CalWildfire.objects.filter(date_time_started__year='2012').count()
    #total_2012_acreage = CalWildfire.objects.filter(date_time_started__year='2012').aggregate(total_acres=Sum('acres_burned'))
    #total_2012_injuries = CalWildfire.objects.filter(date_time_started__year='2012').aggregate(total_injuries=Sum('injuries'))

    total_2012_fires = 5809
    total_2012_acreage = 141154
    total_2012_injuries = 'n/a'

    return render_to_response('index.html', {
        'calwildfires': calwildfires,
        'so_cal_fires': so_cal_fires,
        'so_cal_acreage': so_cal_acreage,
        'total_2012_fires': total_2012_fires,
        'total_2012_acreage': total_2012_acreage,
        'total_2012_injuries': total_2012_injuries,
        'total_2013_fires': total_2013_fires,
        'total_2013_acreage': total_2013_acreage,
        'total_2013_injuries': total_2013_injuries,
    }, context_instance=RequestContext(request))

def detail(request, fire_slug):
    calwildfire = get_object_or_404(CalWildfire, fire_slug=fire_slug)
    calwildfires = CalWildfire.objects.all()[:15]
    wildfire_updates = WildfireUpdate.objects.filter(fire_name__fire_name=calwildfire.fire_name)
    auth1 = tweepy.auth.OAuthHandler(settings.TWEEPY_CONSUMER_KEY, settings.TWEEPY_CONSUMER_SECRET)
    auth1.set_access_token(settings.TWEEPY_ACCESS_TOKEN, settings.TWEEPY_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth1)
    result_list = api.search(calwildfire.twitter_hashtag)

    if calwildfire.asset_host_image_id:
        kpcc_image = search_assethost(settings.ASSETHOST_TOKEN_SECRET, calwildfire.asset_host_image_id)
    else:
        kpcc_image = None

    return render_to_response('detail.html', {
        'calwildfire': calwildfire,
        'calwildfires': calwildfires,
        'wildfire_updates': wildfire_updates,
        'result_list': result_list,
        'kpcc_image': kpcc_image,
    }, context_instance=RequestContext(request))