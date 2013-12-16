from datetime import datetime, date, time, timedelta
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext
from django.db.models import Q, Avg, Max, Min, Sum, Count
from django.utils import simplejson
from calfire_tracker.models import CalWildfire, WildfireUpdate, WildfireTweet
from django.conf import settings
from dateutil import parser
import random
from kpccapi import *
import logging, re

logging.basicConfig(level=logging.DEBUG)

OEMBED_AUTHOR_NAME      = "Fire Tracker, KPCC"
OEMBED_AUTHOR_URL       = "http://www.scpr.org"
EMBED_DEFAULT_WIDTH     = 510
EMBED_DEFAULT_HEIGHT    = 374

FIRE_MAX_CACHE_AGE = (60*60*24)

@xframe_options_sameorigin
def index(request):

    wildfires = CalWildfire.objects.all()
    #lead_fire = CalWildfire.objects.filter(fire_name='Rim Fire')
    calwildfires = wildfires.exclude(containment_percent=None).order_by('containment_percent', '-date_time_started', 'fire_name')[0:20]
    featuredfires = wildfires.filter(promoted_fire=True).order_by('containment_percent', '-date_time_started', 'fire_name')[0:3]
    cache_timestamp = wildfires.all().order_by('-last_saved')

    total_2013_fires = 7009
    total_2013_acreage = 120207
    total_2013_injuries = None

    total_2012_fires = 5809
    total_2012_acreage = 141154
    total_2012_injuries = None

    display_content = ['On the anniversary of the Cedar Fire in San Diego County we look back at the 10 largest wildfires in the state\'s history. <a href="http://projects.scpr.org/firetracker/wildfires/largest-ca-wildfires/" target="_blank"><strong>View the list</strong></a>', 'Learn the terms used by those fighting wildland fires. <a href="http://projects.scpr.org/firetracker/resources/wildland-firefighting-terms/" target="_blank"><strong>Read More</strong></a>', 'How should you care for and protect your pets during a fire? <a href="http://www.humanesociety.org/issues/animal_rescue/tips/pets-disaster.html" target="_blank"><strong>Read More</strong></a>', '2003 wildfires: Memories linger, firefighting techniques evolve after the largest fire in California history. <a href="http://www.scpr.org/news/2013/10/25/39939/2003-wildfires-10-years-after-the-largest-fire-in/" target="_blank"><strong>Read More</strong></a>']

    #cache_expire = (60*60*24)
    cache_expire = (60*15)
    cache_timestamp = cache_timestamp[0].last_saved

    return render_to_response('index.html', {
        'calwildfires': calwildfires,
        'featuredfires': featuredfires,
        'display_content': display_content,
        #'lead_fire': lead_fire,
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
    result_list = WildfireTweet.objects.filter(tweet_hashtag=calwildfire.twitter_hashtag).order_by('-tweet_created_at')[0:15]

    return render_to_response('detail.html', {
        'calwildfire': calwildfire,
        'calwildfires': calwildfires,
        'wildfire_updates': wildfire_updates,
        'result_list': result_list,
        'cache_expire': FIRE_MAX_CACHE_AGE,
    }, context_instance=RequestContext(request))

@xframe_options_exempt
def embeddable(request, fire_slug):
    calwildfire = get_object_or_404(CalWildfire, fire_slug=fire_slug)

    return render_to_response('embeddable.html', {
        'calwildfire': calwildfire,
        'cache_expire': FIRE_MAX_CACHE_AGE,
    }, context_instance=RequestContext(request))

@xframe_options_sameorigin
def archives(request):
    current_year = date.today().year
    calwildfires = CalWildfire.objects.filter(date_time_started__year=current_year).order_by('-date_time_started', 'fire_name')

    return render_to_response('archives.html', {
        'calwildfires': calwildfires,
        'cache_expire': FIRE_MAX_CACHE_AGE,
    })

def largest_ca_fires(request):
    calwildfires = CalWildfire.objects.exclude(containment_percent=None).order_by('-acres_burned', 'fire_name')[0:10]
    return render_to_response('largest_ca_fires.html', {
        'calwildfires': calwildfires,
    })

def oembed(request):
    url     = request.GET.get('url', '')
    width   = request.GET.get('maxwidth', EMBED_DEFAULT_WIDTH)
    height  = request.GET.get('maxheight', EMBED_DEFAULT_HEIGHT)

    if not url:
        return HttpResponseBadRequest(
            ("400 Bad Request: A 'url' parameter is required. "
             "See the oEmbed specfication: http://oembed.com/"),
            content_type="text/plain"
        )

    regex       = re.compile('([^/]+)/?$')
    match       = regex.search(url)
    fire_slug   = match.groups()[0]

    calwildfire = get_object_or_404(CalWildfire, fire_slug=fire_slug)

    embed_html = ("<iframe width=\"100%%\" height=\"%s\" scrolling=\"no\" "
                  "frameborder=\"no\" src=\"%s%sembed\"></iframe>") % (
                 height, settings.SITE_URL, calwildfire.get_absolute_url())

    data = {
        'type'              : 'rich',
        'version'           : '1.0',
        'title'             : calwildfire.fire_name,
        'author_name'       : OEMBED_AUTHOR_NAME,
        'author_url'        : OEMBED_AUTHOR_URL,
        'provider_name'     : OEMBED_AUTHOR_NAME,
        'provider_url'      : OEMBED_AUTHOR_URL,
        'cache_age'         : FIRE_MAX_CACHE_AGE,
        'note'              : ("This widget is fully responsive. "
                               "A 100% width should be used."),
        'html'              : embed_html,
        'width'             : width,
        'height'            : height
    }

    return HttpResponse(json.dumps(data), content_type="application/json")