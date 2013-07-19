from django.conf.urls.defaults import *
from calfire_tracker.views import index, detail, archives

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
)