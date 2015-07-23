"""
Django settings for firetracker project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

ADMINS = (
    ("Chris Keller", "ckeller@scpr.org"),
)

SEND_BROKEN_LINK_EMAILS = True

MANAGERS = ADMINS

TIME_ZONE = "America/Los_Angeles"

LANGUAGE_CODE = "en-us"

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

TEMPLATE_DIRS = (os.path.join(SITE_ROOT, "templates"),)

TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
#     "django.template.loaders.eggs.Loader",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

MIDDLEWARE_CLASSES = (
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "calfire_tracker.middleware.XsSharing",
)

ROOT_URLCONF = "firetracker.urls"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.flatpages",
    "django.contrib.redirects",
    "django.contrib.humanize",

    # apps
    "calfire_tracker",

    # api & tools
    "south",
    "django_admin_bootstrapped",
    "massadmin",
    "tastypie",
    "commander",

    # admin
    "django.contrib.admin",
    "django.contrib.admindocs",
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    "version": 1,

    "disable_existing_loggers": True,

    "formatters": {
        "verbose": {
            "format" : "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
            "datefmt" : "%d/%b/%Y %H:%M:%S"
        },
        "simple": {
            "format": "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s"
        },
    },

    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },

        "null": {
            "level": "DEBUG",
            "class":"django.utils.log.NullHandler",
        },

        #"file": {
            #"level": "DEBUG",
            #"class": "logging.FileHandler",
            #"filename": "mysite.log",
            #"formatter": "verbose"
        #},

    },

    "loggers": {
        "firetracker": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },

        "django.db.backends": {
            "handlers": ["null"],
            "level": "DEBUG",
            "propagate": False,
        },

    }
}

TEST_RUNNER = "django.test.simple.DjangoTestSuiteRunner"

AUTH_PROFILE_MODULE = "create_user.UserProfile"

# Honor the "X-Forwarded-Proto" header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

XS_SHARING_ALLOWED_ORIGINS = "*"
XS_SHARING_ALLOWED_METHODS = "GET"
