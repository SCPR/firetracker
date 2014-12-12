# Django settings for firetracker project.

# -*- coding: utf-8 -*-
import os
from os.path import expanduser
from settings_common import *
import yaml

CONFIG_FILE     = os.environ.setdefault("FIRETRACKER_CONFIG_PATH","./development.yml")
CONFIG = yaml.load(open(CONFIG_FILE))

DEBUG = CONFIG.get('debug',False)
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE'    : 'django.db.backends.mysql',
        'NAME'      : CONFIG['database']['database'],
        'USER'      : CONFIG['database']['username'],
        'PASSWORD'  : CONFIG['database']['password'],
        'HOST'      : CONFIG['database']['host'],
        'PORT'      : CONFIG['database']['port']
    }
}

SECRET_KEY = CONFIG['secret_key']

TWEEPY_CONSUMER_KEY         = CONFIG['api']['tweepy']['consumer_key']
TWEEPY_CONSUMER_SECRET      = CONFIG['api']['tweepy']['consumer_secret']
TWEEPY_ACCESS_TOKEN         = CONFIG['api']['tweepy']['access_token']
TWEEPY_ACCESS_TOKEN_SECRET  = CONFIG['api']['tweepy']['access_token_secret']

ASSETHOST_TOKEN_SECRET = CONFIG['api']['assethost']['token_secret']

# auth to send out emails when models change

if 'email' in CONFIG:
    EMAIL_HOST              = CONFIG['email']['host']
    EMAIL_HOST_USER         = CONFIG['email']['user']
    EMAIL_HOST_PASSWORD     = CONFIG['email']['password']
    EMAIL_PORT              = CONFIG['email']['port']
    EMAIL_USE_TLS           = CONFIG['email']['use_tls']


CACHES = {
    "default": {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '%s:%s:%s' % (
            CONFIG['cache']['host'],
            CONFIG['cache']['port'],
            CONFIG['cache']['db']
        ),
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
        }
    }
}

ADMIN_MEDIA_PREFIX = '/media/'

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
STATIC_ROOT = os.path.join(SITE_ROOT, "public", "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

SITE_URL = 'http://firetracker.scpr.org'

# Additional locations of static files
STATICFILES_DIRS = (

)
