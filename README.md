## Fire Tracker

### Initial Setup

* Create a new virtualenv firetracker

        mkvirtualenv firetracker

* Install dependencies from requirements.txt. You'll have to first remove titlecase==0.5.1 as a dependency has to be installed first.

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
        local_settings.py

* Adjust settings.py params, enable admin and add south to INSTALLED_APPS

* Enable the admin in firetracker/urls.py

* Sync the database

        python manage.py syncdb
