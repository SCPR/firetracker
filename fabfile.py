from __future__ import with_statement
import os
import time, datetime
from fabric.operations import prompt
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import green

env.user  = 'archive'
env.hosts = ['66.226.4.228']

REMOTE_APP_ROOT = '/web/archive/apps/firetracker/firetracker'


def restart():
    """
    Restarts the server
    """
    with cd(REMOTE_APP_ROOT):
        run('mkdir -p tmp/ && touch tmp/restart.txt')


def update_code():
    """
    Updates the code on the remote server
    """
    with cd(REMOTE_APP_ROOT):
        run('git pull')


def deploy():
    """
    Pulls the latest code from source control & restarts the server
    """
    with cd(REMOTE_APP_ROOT):
        update_code()
        restart()


def migrate(*args):
    """
    Execute south migrations (takes arguments)
    """
    with cd(REMOTE_APP_ROOT):
        run(("/web/archive/apps/firetracker/"
            "virtualenv/firetracker/bin/python "
            "manage.py migrate ") + " ".join(args))


def revert():
    """
    Revert git via reset --hard @{1}
    """
    with cd(REMOTE_APP_ROOT):
        run('git reset --hard @{1}')
        restart()


def schema(params='auto'):
    local('python manage.py schemamigration calfire_tracker --' + params)
    local('python manage.py migrate calfire_tracker')


def scrape():
    local('python manage.py scraper_wildfires')


def archives():
    local('python manage.py v3_scraper_wildfires')


def convert():
    local('python manage.py convert_to_south calfire_tracker')
