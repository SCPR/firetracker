# Django settings for firetracker project.

# -*- coding: utf-8 -*-
import os
from os.path import expanduser
from settings_common import *
import yaml

DEBUG = False
TEMPLATE_DEBUG = DEBUG

env = 'production'

CONFIG_DB       = yaml.load(open("config/database.yml", 'r'))[env]
CONFIG_CACHE    = yaml.load(open("config/cache.yml", 'r'))[env]
CONFIG_APP      = yaml.load(open("config/app.yml", 'r'))[env]
CONFIG_API      = yaml.load(open("config/api.yml", 'r'))[env]
CONFIG_EMAIL    = yaml.load(open("config/email.yml", 'r'))[env]

DATABASES = {
    'default': {
        'ENGINE'    : 'django.db.backends.mysql',
        'NAME'      : CONFIG_DB['database'],
        'USER'      : CONFIG_DB['username'],
        'PASSWORD'  : CONFIG_DB['password'],
        'HOST'      : CONFIG_DB['host'],
        'PORT'      : CONFIG_DB['port']
    }
}

SECRET_KEY = CONFIG_APP['secret_key']

TWEEPY_CONSUMER_KEY         = CONFIG_API['tweepy']['consumer_key']
TWEEPY_CONSUMER_SECRET      = CONFIG_API['tweepy']['consumer_secret']
TWEEPY_ACCESS_TOKEN         = CONFIG_API['tweepy']['access_token']
TWEEPY_ACCESS_TOKEN_SECRET  = CONFIG_API['tweepy']['access_token_secret']

ASSETHOST_TOKEN_SECRET = CONFIG_API['assethost']['token_secret']

# auth to send out emails when models change
EMAIL_HOST              = CONFIG_EMAIL['host']
EMAIL_HOST_USER         = CONFIG_EMAIL['user']
EMAIL_HOST_PASSWORD     = CONFIG_EMAIL['password']
EMAIL_PORT              = CONFIG_EMAIL['port']
EMAIL_USE_TLS           = CONFIG_EMAIL['use_tls']


CACHES = {
    "default": {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '%s:%s:%s' % (
            CONFIG_CACHE['host'],
            CONFIG_CACHE['port'],
            CONFIG_CACHE['db']
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
