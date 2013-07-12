from django.conf.urls.defaults import *
from calfire_tracker.views import index, detail, tweetstream

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
        regex   = r'^test/tweets/$',
        view    = tweetstream,
        kwargs  = {},
        name    = 'tweetstream',
    ),

)