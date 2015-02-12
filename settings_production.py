# Django settings for firetracker project.

# -*- coding: utf-8 -*-
import os
from os.path import expanduser
from settings_common import *
import pytz
from pytz import timezone
import yaml

CONFIG_FILE = os.environ.setdefault("CONFIG_PATH","./development.yml")
CONFIG = yaml.load(open(CONFIG_FILE))

DEBUG = CONFIG.get("debug", False)
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = DEBUG

INTERNAL_IPS = CONFIG.get("internal_ips", [])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": CONFIG["database"]["database"],
        "USER": CONFIG["database"]["username"],
        "PASSWORD": CONFIG["database"]["password"],
        "HOST": CONFIG["database"]["host"],
        "PORT": CONFIG["database"]["port"]
    }
}

SECRET_KEY = CONFIG["secret_key"]

# tweepy api though should change this
TWEEPY_CONSUMER_KEY = CONFIG["api"]["tweepy"]["consumer_key"]
TWEEPY_CONSUMER_SECRET = CONFIG["api"]["tweepy"]["consumer_secret"]
TWEEPY_ACCESS_TOKEN = CONFIG["api"]["tweepy"]["access_token"]
TWEEPY_ACCESS_TOKEN_SECRET = CONFIG["api"]["tweepy"]["access_token_secret"]

REQUEST_HEADERS = {
    "From": CONFIG["api"]["headers"]["from"],
    "User-agent": CONFIG["api"]["headers"]["user_agent"]
}

# assethost api token
ASSETHOST_TOKEN_SECRET = CONFIG["api"]["assethost"]["token_secret"]

# auth to send out emails when models change
if "email" in CONFIG:
    EMAIL_HOST = CONFIG["email"]["host"]
    EMAIL_HOST_USER = CONFIG["email"]["user"]
    EMAIL_HOST_PASSWORD = CONFIG["email"]["password"]
    EMAIL_PORT = CONFIG["email"]["port"]
    EMAIL_USE_TLS = CONFIG["email"]["use_tls"]

CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = (60 * 5)
CACHE_MIDDLEWARE_KEY_PREFIX = ""

# django debug toolbar configuration
if DEBUG_TOOLBAR:

    # debugging toolbar middleware
    MIDDLEWARE_CLASSES += (
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )

    # javascript panels for the development debugging toolbar
    #DEBUG_TOOLBAR_PANELS = (
        #"debug_toolbar.panels.versions.VersionsPanel",
        #"debug_toolbar.panels.timer.TimerPanel",
        #"debug_toolbar.panels.settings.SettingsPanel",
        #"debug_toolbar.panels.headers.HeadersPanel",
        #"debug_toolbar.panels.request.RequestPanel",
        #"debug_toolbar.panels.profiling.ProfilingPanel",
        #"debug_toolbar.panels.sql.SQLPanel",
        #"debug_toolbar.panels.staticfiles.StaticFilesPanel",
        #"debug_toolbar.panels.templates.TemplatesPanel",
        #"debug_toolbar.panels.cache.CachePanel",
        #"debug_toolbar.panels.signals.SignalsPanel",
        #"debug_toolbar.panels.logging.LoggingPanel",
        #"debug_toolbar.panels.redirects.RedirectsPanel",
    #)

    # Debug toolbar app
    INSTALLED_APPS += ("debug_toolbar",)

    CONFIG_DEFAULTS = {
        "SHOW_COLLAPSED": False,
        "SQL_WARNING_THRESHOLD": 500,
        "INTERCEPT_REDIRECTS": False,
        "SHOW_TOOLBAR_CONFIG": (lambda: DEBUG)
    }

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

else:
    CACHES = {
        "default": {
            "BACKEND": "redis_cache.cache.RedisCache",
            "LOCATION": "%s:%s:%s" % (
                CONFIG["cache"]["host"],
                CONFIG["cache"]["port"],
                CONFIG["cache"]["db"]
            ),
            "OPTIONS": {
                "CLIENT_CLASS": "redis_cache.client.DefaultClient",
            }
        }
    }

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "firetracker.wsgi.application"

ADMIN_MEDIA_PREFIX = "/media/"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ""

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ""

# Absolute path to the directory static files should be collected to.
# Don"t put anything in this directory yourself; store your static files
# in apps" "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, "public", "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

SITE_URL = "http://firetracker.scpr.org"

# Additional locations of static files
STATICFILES_DIRS = (

)
