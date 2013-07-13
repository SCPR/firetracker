# Django settings for firetracker project.

# -*- coding: utf-8 -*-
import os
from os.path import expanduser
from settings_common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

execfile(expanduser('~/apps/firetracker/.production_settings'))


ADMIN_MEDIA_PREFIX = '/firetracker/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/web/archive/apps/firetracker/firetracker/public/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/firetracker/static/'

# Additional locations of static files
STATICFILES_DIRS = (

)
