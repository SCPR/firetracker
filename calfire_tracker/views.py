from datetime import datetime, date, time, timedelta
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext
from calfire_tracker.models import CalWildfire

def index(request):
    calwildfires = CalWildfire.objects.all()
    return render_to_response('index.html', {'calwildfires': calwildfires},
        context_instance=RequestContext(request))

def detail(request, fire_slug):
    fire_detail = get_object_or_404(CalWildfire, fire_slug=fire_slug)
    startdate = date.today()
    enddate = timedelta(days=21)
    displaydate = startdate - enddate
    calwildfires = CalWildfire.objects.filter(date_time_started__gte=displaydate)
    return render_to_response('detail.html', {'calwildfire': fire_detail, 'calwildfires': calwildfires},
        context_instance=RequestContext(request))