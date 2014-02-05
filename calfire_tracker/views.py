from datetime import datetime, date, time, timedelta
from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext, Context, loader
from django.db.models import Q, Avg, Max, Min, Sum, Count
from django.utils import simplejson
from calfire_tracker.models import CalWildfire, WildfireUpdate, WildfireTweet, WildfireAnnualReview, WildfireDisplayContent
from django.conf import settings
from dateutil import parser
from random import randint
import logging, re, json

logging.basicConfig(format='\033[1;36m%(levelname)s:\033[0;37m %(message)s', level=logging.DEBUG)

OEMBED_AUTHOR_NAME      = "Fire Tracker, KPCC"
OEMBED_AUTHOR_URL       = "http://www.scpr.org"
EMBED_DEFAULT_WIDTH     = 510
EMBED_DEFAULT_HEIGHT    = 374

FIRE_MAX_CACHE_AGE = (60*60*24)

@xframe_options_sameorigin
def index(request):
    wildfires = CalWildfire.objects.all()
    calwildfires = wildfires.exclude(containment_percent=None).order_by('containment_percent', '-date_time_started', 'fire_name')[0:20]
    featuredfires = wildfires.filter(promoted_fire=True).order_by('containment_percent', '-date_time_started', 'fire_name')[0:3]
    cache_timestamp = wildfires.all().order_by('-last_saved')
    current_year = date.today().year
    last_year = date.today().year-1
    year_over_year_comparison = WildfireAnnualReview.objects.filter(
        Q(year=current_year, jurisdiction='CalFire') | Q(year=last_year, jurisdiction='CalFire')
    )
    count = WildfireDisplayContent.objects.filter(display_content_type=True).count()
    random_index = randint(0, count-1)
    display_content = WildfireDisplayContent.objects.filter(display_content_type=True)[random_index]
    cache_expire = (60*5)
    cache_timestamp = cache_timestamp[0].last_saved
    return render_to_response('index.html', {
        'calwildfires': calwildfires,
        'featuredfires': featuredfires,
        'display_content': display_content,
        'year_over_year_comparison': year_over_year_comparison,
        'cache_expire': cache_expire,
        'cache_timestamp': cache_timestamp
    })

@xframe_options_sameorigin
def detail(request, fire_slug):
    calwildfire = get_object_or_404(CalWildfire, fire_slug=fire_slug)
    calwildfires = CalWildfire.objects.exclude(containment_percent=None).order_by('-date_time_started', 'fire_name', 'containment_percent')[0:15]
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

    # get unique values for years that are in the database
    #list_of_wildfire_years = CalWildfire.objects.values('year').distinct().order_by('-year')
    #for year in list_of_wildfire_years:
        #year['queryset'] = CalWildfire.objects.filter(date_time_started__year=year['year']).order_by('-date_time_started', 'fire_name')
    #for fire in list_of_wildfire_years:
        #logging.debug(fire)

    # pulls rev chron of all the fires in the database
    calwildfires = CalWildfire.objects.all().order_by('-date_time_started', 'fire_name')
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

def custom_403(request):
    wildfires = CalWildfire.objects.all()
    calwildfires = wildfires.exclude(containment_percent=None).order_by('-date_time_started', 'fire_name')[0:20]
    template = loader.get_template('403.html')
    context = Context({'calwildfires': calwildfires})
    return HttpResponse(
        content=template.render(context),
        content_type='text/html; charset=utf-8',
        status=403
    )

def custom_404(request):
    wildfires = CalWildfire.objects.all()
    calwildfires = wildfires.exclude(containment_percent=None).order_by('-date_time_started', 'fire_name')[0:20]
    template = loader.get_template('404.html')
    context = Context({'calwildfires': calwildfires})
    return HttpResponse(
        content=template.render(context),
        content_type='text/html; charset=utf-8',
        status=404
    )

def custom_500(request):
    wildfires = CalWildfire.objects.all()
    calwildfires = wildfires.exclude(containment_percent=None).order_by('-date_time_started', 'fire_name')[0:20]
    template = loader.get_template('500.html')
    context = Context({'calwildfires': calwildfires})
    return HttpResponse(
        content=template.render(context),
        content_type='text/html; charset=utf-8',
        status=500
    )