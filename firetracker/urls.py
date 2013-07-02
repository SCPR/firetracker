# This also imports the include function
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView

# tastypie API includes
#from tastypie.api import Api
#from firetracker.api import WildfireResource

# enable the admin
from django.contrib import admin
admin.autodiscover()

# invoke the api
#v1_api = Api(api_name='v1')
#v1_api.register(WildfireResource())

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

	# batch edit
	(r'^admin/', include('massadmin.urls')),

	# tastypie API
	#url(r'^api/', include(v1_api.urls)),

	# csv importer
    (r'^import/', include('csvimporter.urls')),

    # data_exports
    url(r'^exports/', include('data_exports.urls', namespace='data_exports')),

	# app urls
    #(r'^wildfires/', include('wildfires.urls')),

)