from django.conf.urls.defaults import *
from calfire_tracker.views import index, detail, archives, about_data

urlpatterns = patterns('',
    url(
        regex   = r'^$',
        view    = index,
        kwargs  = {},
        name    = 'index',
    ),

    url(
        regex   = r'^(?P<fire_slug>[-\w]+)/$',
        view    = detail,
        kwargs  = {},
        name    = 'detail',
    ),

    url(
        regex   = r'^wildfires/archives/$',
        view    = archives,
        kwargs  = {},
        name    = 'archives',
    ),

    url(
        regex   = r'^about/about-the-data/$',
        view    = about_data,
        kwargs  = {},
        name    = 'about_data',
    ),

)