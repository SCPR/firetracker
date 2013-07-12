from __future__ import with_statement
import os
import time, datetime
from fabric.operations import prompt
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import green

env.user            = 'archive'
env.hosts           = ['66.226.4.228']
env.project_root    = '/web/archive/apps/firetracker/firetracker'
env.python_exe      = "/web/archive/apps/firetracker/virtualenv/firetracker/bin/python"

def update_code():
    """
    Updates the code on the remote server
    """
    with cd(env.project_root):
        run('git pull')


def restart():
    """
    Restarts the server
    """
    with cd(env.project_root):
        run('mkdir -p tmp/ && touch tmp/restart.txt')


def setup_static_files():
    """
    Handle the static assets on the remote server.
    """
    with cd(env.project_root)
        run("%s manage.py collectstatic --noinput" % env.python_exe)


def deploy():
    """
    Pulls the latest code from source control & restarts the server
    """
    with cd(env.project_root):
        update_code()
        setup_static_files()
        restart()


def migrate(*args):
    """
    Execute south migrations (takes arguments)
    """
    with cd(env.project_root):
        run("%s manage.py migrate " % env.python_exe) + " ".join(args))


def revert():
    """
    Revert git via reset --hard @{1}
    """
    with cd(env.project_root):
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
