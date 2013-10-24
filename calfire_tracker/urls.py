from django.conf.urls.defaults import *
from calfire_tracker.views import oembed, index, detail, embeddable, archives, topTwenty

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
        regex   = r'^wildfires/top-twenty-largest-ca-wildfires/$',
        view    =  topTwenty,
        kwargs  = {},
        name    = 'topTwenty',
    ),

)
