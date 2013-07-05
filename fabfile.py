from __future__ import with_statement
import os
import time, datetime
from fabric.operations import prompt
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import green

def sync():
    local('python manage.py syncdb')

def run():
    local('python manage.py runserver')

def schema(params='initial'):
    local('python manage.py schemamigration calfire_tracker --' + params)
    local('python manage.py migrate calfire_tracker')

def scrape():
    local('python manage.py scraper_wildfires')

def archives():
    local('python manage.py v3_scraper_wildfires')