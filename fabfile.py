from __future__ import with_statement
import os
import time, datetime
from fabric.operations import prompt
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import green

def scrape():
    local('python manage.py scraper_wildfires')
    local('heroku run python manage.py scraper_wildfires')

def model_changed():
    local('git cma "updates to models schema')

    local('python manage.py convert_to_south wildfires')
    local('python manage.py schemamigration wildfires --initial')
    local('python manage.py migrate wildfires --fake')

    local('git add .')
    local('git cma "adds migration file')
    local('git push')

    local('heroku run python manage.py convert_to_south wildfires')
    local('heroku run python manage.py schemamigration wildfires --initial')
    local('heroku run python manage.py migrate wildfires --fake')

def heroku_reset():
    heroku pg:reset DATABASE