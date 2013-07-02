# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext
from calfire_tracker.models import CalWildfire

#the main index request
def index(request):

    #tells how the output should be structured
    calwildfire_listing = CalWildfire.objects.all()

    #takes template name as first argument
    #returns an HttpResponse object of the given template
    return render_to_response('index.html', {'calwildfire_listing': calwildfire_listing})

#details request
def detail(request, fire_slug):
    fire_detail = get_object_or_404(CalWildfire, fire_slug=fire_slug)
    return render_to_response('detail.html', {'calwildfire': fire_detail},
        context_instance=RequestContext(request))