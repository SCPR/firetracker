from datetime import datetime, date, time, timedelta
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext
from django.db.models import Q, Avg, Max, Min, Sum, Count
from calfire_tracker.models import CalWildfire, WildfireUpdate
import tweepy

def index(request):
    calwildfires = CalWildfire.objects.all().order_by('-date_time_started', 'fire_name')
    so_cal_counties = CalWildfire.objects.filter(Q(county='Los Angeles County') | Q(county='Orange County') | Q(county='Riverside County') | Q(county='San Bernardino County') | Q(county='Ventura County'))
    so_cal_fires = so_cal_counties.filter(date_time_started__year='2013').count()
    so_cal_acreage = so_cal_counties.filter(date_time_started__year='2013').aggregate(total_acres=Sum('acres_burned'))
    total_2013_fires = CalWildfire.objects.filter(date_time_started__year='2013').count()
    total_2013_acreage = CalWildfire.objects.filter(date_time_started__year='2013').aggregate(total_acres=Sum('acres_burned'))
    total_2013_injuries = CalWildfire.objects.filter(date_time_started__year='2013').aggregate(total_injuries=Sum('injuries'))
    total_2012_fires = CalWildfire.objects.filter(date_time_started__year='2012').count()
    total_2012_acreage = CalWildfire.objects.filter(date_time_started__year='2012').aggregate(total_acres=Sum('acres_burned'))
    total_2012_injuries = CalWildfire.objects.filter(date_time_started__year='2012').aggregate(total_injuries=Sum('injuries'))
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
    startdate = date.today()
    enddate = timedelta(days=60)
    displaydate = startdate - enddate
    calwildfires = CalWildfire.objects.filter(date_time_started__gte=displaydate)
    wildfire_updates = WildfireUpdate.objects.filter(fire_name__fire_name=calwildfire.fire_name)
    api = tweepy.API(auth1)
    result_list = api.search(calwildfire.twitter_hashtag)
    return render_to_response('detail.html', {
        'calwildfire': calwildfire,
        'calwildfires': calwildfires,
        'wildfire_updates': wildfire_updates,
        'result_list': result_list,
    }, context_instance=RequestContext(request))