from __future__ import with_statement
import os
import time, datetime, logging
from fabric.operations import prompt
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import green

env.user            = 'archive'
env.hosts           = ['66.226.4.228']
env.project_root    = '/web/archive/apps/firetracker/firetracker'
env.python_exe      = "/web/archive/apps/firetracker/virtualenvs/firetracker/bin/python"

logging.basicConfig(format='\033[1;36m%(levelname)s:\033[0;37m %(message)s', level=logging.DEBUG)

# production functions
def update_code():
    # production function to update the code on the remote server
    with cd(env.project_root):
        run('git pull')

def restart():
    # production function to restart the server
    with cd(env.project_root):
        run('mkdir -p tmp/ && touch tmp/restart.txt')

def collectstatic():
    # production function to handle the static assets on the remote server
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py collectstatic --noinput" % env.python_exe)

def deploy():
    # production function to pull the latest code from source control & restarts the server
    with cd(env.project_root):
        update_code()
        collectstatic()
        restart()

def migrate(*args):
    #production function to execute south migrations (takes arguments)
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py migrate " % env.python_exe) + " ".join(args)

def revert():
    # production function to revert git via reset --hard @{1}
    with cd(env.project_root):
        run('git reset --hard @{1}')
        collectstatic()
        restart()

def server_scrape():
    # production function to manually run the scraper on the remote server
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py scraper_wildfires" % env.python_exe)

def server_update_ids():
    # production function to manually run the scraper on the remote server
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py update_fire_ids" % env.python_exe)

def server_tweets():
    # production function to manually poll twitter on the remote server
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py tweepy_to_db" % env.python_exe)

def server_fixture_dump(model=''):
    # dumps fixtures file of wildfires in the database
    # ex usage:
        # fab server_fixture_dump:'calwildfire'
        # fab server_fixture_dump:'wildfireupdate'
        # fab server_fixture_dump:'wildfiretweet'
        # fab server_fixture_dump:'wildfireannualreview'
        # fab server_fixture_dump:'wildfiredisplaycontent'
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py dumpdata calfire_tracker.%s --indent=2 > bak_%s.json" % (env.python_exe, model, model))

def server_fixture_load(model=''):
    # dumps fixtures file of wildfires in the database
    # ex usage:
        # fab server_fixture_load:'calwildfire'
        # fab server_fixture_load:'wildfireupdate'
        # fab server_fixture_load:'wildfiretweet'
        # fab server_fixture_load:'wildfireannualreview'
        # fab server_fixture_load:'wildfiredisplaycontent'
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py loaddata bak_%s.json" % (env.python_exe, model))

def server_sync_data_with_local(model=''):
    # pulls data for older fires from development, uploads to server
    # runs management command to backup, runs runs management command to load
    # ex usage:
        # fab server_sync_data_with_local:'calwildfire'
        # fab server_sync_data_with_local:'wildfireupdate'
        # fab server_sync_data_with_local:'wildfiretweet'
        # fab server_sync_data_with_local:'wildfireannualreview'
        # fab server_sync_data_with_local:'wildfiredisplaycontent'
    local("python manage.py dumpdata calfire_tracker.%s --indent=2 > bak_%s.json" % (model, model))
    local("scp ~/Programming/2kpcc/django-projects/firetracker/bak_%s.json archive@media:/web/archive/apps/firetracker/firetracker" % (model))
    with cd(env.project_root):
        with shell_env(DJANGO_SETTINGS_MODULE='settings_production'):
            run("%s manage.py loaddata bak_%s.json" % (env.python_exe, model))

#### ####

# development functions
def localrun():
    # runs local dev server
    local("python manage.py runserver")

def localscrape():
    # production function to manually run the scraper in local environment
    local("python manage.py scraper_wildfires")

def localupdateids():
    # production function to manually run the scraper in local environment
    local("python manage.py update_fire_ids")

def localschema():
    # production function to manually run the scraper in local environment
    local("python manage.py schemamigration calfire_tracker --auto")

def localmigrate():
    # production function to manually run the scraper in local environment
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

def local_sync_data_with_server():
    # dumps server data as a fixture for a given model down to local environment and loads
    server_fixture_dump('calwildfire')
    local("scp archive@media:/web/archive/apps/firetracker/firetracker/bak_calwildfire.json .")
    local("python manage.py loaddata bak_calwildfire.json")

    server_fixture_dump('wildfireupdate')
    local("scp archive@media:/web/archive/apps/firetracker/firetracker/bak_wildfireupdate.json .")
    local("python manage.py loaddata bak_wildfireupdate.json")

    server_fixture_dump('wildfiretweet')
    local("scp archive@media:/web/archive/apps/firetracker/firetracker/bak_wildfiretweet.json .")
    local("python manage.py loaddata bak_wildfiretweet.json")

    server_fixture_dump('wildfireannualreview')
    local("scp archive@media:/web/archive/apps/firetracker/firetracker/bak_wildfireannualreview.json .")
    local("python manage.py loaddata bak_wildfireannualreview.json")

    server_fixture_dump('wildfiredisplaycontent')
    local("scp archive@media:/web/archive/apps/firetracker/firetracker/bak_wildfiredisplaycontent.json .")
    local("python manage.py loaddata bak_wildfiredisplaycontent.json")