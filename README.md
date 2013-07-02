## Fire Tracker

### Initial Setup

* Create a new virtualenv firetracker

        mkvirtualenv firetracker

* Install dependencies from requirements.txt. You'll have to first remove titlecase==0.5.1 as a dependency has to be installed first and I haven't found a way around this.

        pip install -r requirements.txt

* Re-run to install titlecase==0.5.1

        pip install -r requirements.txt

* Create firetracker project

        django-admin.py startproject firetracker .

* Add a .gitignore file

        .DS_Store
        venv
        *.pyc
        *.sqlite
        *.csv
        project_scratchpad.md

* Adjust settings.py params, enable admin and add south to INSTALLED_APPS

* Add settings to top of settings.py

        # -*- coding: utf-8 -*-
        # Django settings for firetracker project.
        import os
        import dj_database_url
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

* Add db informaton to your settings.py to deal with heroku deployment

        DATABASES = {
            'default': dj_database_url.config(default='sqlite:///firetracker.sqlite')
        }

* Enable the admin in firetracker/urls.py

* Sync the database and create the superuser account

        python manage.py syncdb
        
* Enable django_admin_bootstrapped in INSTALLED_APPS

* Enable massadmin, csvimporter and data_exports in INSTALLED_APPS

* Add URLs for these apps to urls.py after admin URLs

        # batch edit
        (r'^admin/', include('massadmin.urls')),
        
        # csv importer
        (r'^import/', include('csvimporter.urls')),
        
        # data_exports
        url(r'^exports/', include('data_exports.urls', namespace='data_exports')),

### Creating the CalFire application



