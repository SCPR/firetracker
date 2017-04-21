from __future__ import with_statement
import os
import time
import datetime
import logging
from fabric.operations import prompt
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import green

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

# development functions
def run():
    # runs local dev server
    local("python manage.py runserver")

def test():
    # shortcut for running tests
    local("python manage.py test calfire_tracker")

def scrape():
    # production function to manually run the scraper in local environment
    local("python manage.py scraper_wildfires")

def updateids():
    local("python manage.py update_fire_ids")

def schema():
    local("python manage.py schemamigration calfire_tracker --auto")

def localmigrate():
    local("python manage.py migrate calfire_tracker")

def localtweets():
    # production function to manually poll twitter in local environment
    local("python manage.py tweepy_to_db")

def localfixture_dump(model=''):
    # dumps fixtures file of wildfires in the database
    # ex usage:
        # fab local_fixture_dump:'calwildfire'
        # fab local_fixture_dump:'wildfireupdate'
        # fab local_fixture_dump:'wildfiretweet'
        # fab local_fixture_dump:'wildfireannualreview'
        # fab local_fixture_dump:'wildfiredisplaycontent'
    local("python manage.py dumpdata calfire_tracker.%s --indent=2 > bak_%s.json" % (model, model))

def localfixture_load(model=''):
    # dumps fixtures file of wildfires in the database
    # ex usage:
        # fab local_fixture_load:'calwildfire'
        # fab local_fixture_load:'wildfireupdate'
        # fab local_fixture_load:'wildfiretweet'
        # fab local_fixture_load:'wildfireannualreview'
        # fab local_fixture_load:'wildfiredisplaycontent'
    local("python manage.py loaddata bak_%s.json" % (model))

def __env_cmd(cmd):
    return env.bin_root + cmd
