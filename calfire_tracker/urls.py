from django.conf.urls.defaults import *
from calfire_tracker.views import oembed, index, detail, embeddable, archives, largest_ca_fires

urlpatterns = patterns('',
    url(
        regex   = r'^oembed/?$',
        view    = oembed,
    ),

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
        regex   = r'^(?P<fire_slug>[-\w]+)/embed/$',
        view    = embeddable,
        kwargs  = {},
        name    = 'embeddable',
    ),

    url(
        regex   = r'^wildfires/archives/$',
        view    = archives,
        kwargs  = {},
        name    = 'archives',
    ),

    url(
        regex   = r'^wildfires/largest-ca-wildfires/$',
        view    =  largest_ca_fires,
        kwargs  = {},
        name    = 'largest_ca_fires',
    ),

)
