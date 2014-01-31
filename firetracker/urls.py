# This also imports the include function
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView

# tastypie API includes
from tastypie.api import Api
from firetracker.api import CalWildfireResource

# enable the admin
from django.contrib import admin
admin.autodiscover()

# invoke the api
v1_api = Api(api_name='v1')
v1_api.register(CalWildfireResource())

handler403 = 'calfire_tracker.views.custom_403'
handler404 = 'calfire_tracker.views.custom_404'
handler500 = 'calfire_tracker.views.custom_500'

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

	# batch edit
	url(r'^admin/', include('massadmin.urls')),

	# tastypie API
	url(r'^api/', include(v1_api.urls)),

    # url pattern to kick root to index of firetracker application
    url(r'', include('calfire_tracker.urls')),
)