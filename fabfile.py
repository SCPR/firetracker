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


def collectstatic():
    """
    Handle the static assets on the remote server.
    """
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py collectstatic --noinput" % env.python_exe)


def deploy():
    """
    Pulls the latest code from source control & restarts the server
    """
    with cd(env.project_root):
        update_code()
        collectstatic()
        restart()


def migrate(*args):
    """
    Execute south migrations (takes arguments)
    """
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py migrate " % env.python_exe) + " ".join(args)


def revert():
    """
    Revert git via reset --hard @{1}
    """
    with cd(env.project_root):
        run('git reset --hard @{1}')
        collectstatic()
        restart()

def scrape():
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py scraper_wildfires" % env.python_exe)

# local fab commands
def local_scrape():
    local("%s manage.py scraper_wildfires" % env.python_exe)

def archives():
    local('%s manage.py v3_scraper_wildfires' % env.python_exe)