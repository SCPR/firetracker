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
env.python_exe      = "/web/archive/apps/firetracker/virtualenvs/firetracker/bin/python"

# production functions
def update_code():
    """
    Production function to update the code on the remote server
    """
    with cd(env.project_root):
        run('git pull')


def restart():
    """
    Production function to restart the server
    """
    with cd(env.project_root):
        run('mkdir -p tmp/ && touch tmp/restart.txt')


def collectstatic():
    """
    Production function to handle the static assets on the remote server.
    """
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py collectstatic --noinput" % env.python_exe)


def deploy():
    """
    Production function to pull the latest code from source control & restarts the server
    """
    with cd(env.project_root):
        update_code()
        collectstatic()
        restart()


def migrate(*args):
    """
    Production function to execute south migrations (takes arguments)
    """
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py migrate " % env.python_exe) + " ".join(args)


def revert():
    """
    Production function to revert git via reset --hard @{1}
    """
    with cd(env.project_root):
        run('git reset --hard @{1}')
        collectstatic()
        restart()

def scrape():
    """
    Production function to manually run the scraper on the remote server
    """
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py scraper_wildfires" % env.python_exe)

# development functions
def local_run():
    """
    Runs local dev server
    """
    local("python manage.py runserver")

def local_scrape():
    """
    Runs scraper for local database
    """
    local("python manage.py scraper_wildfires")