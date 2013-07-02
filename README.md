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

* Enable the admin in firetracker/urls.py

        # This also imports the include function
        from django.conf import settings
        from django.conf.urls.defaults import *
        from django.views.generic.simple import direct_to_template
        from django.core.urlresolvers import reverse
        from django.views.generic.base import RedirectView
        
        # enable the admin
        from django.contrib import admin
        admin.autodiscover()
        
        urlpatterns = patterns('',
        
            # Uncomment the admin/doc line below to enable admin documentation:
            url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        
            # Uncomment the next line to enable the admin:
            url(r'^admin/', include(admin.site.urls)),
        )

* Create a local_settings.py file for local development and add the following

        DATABASES = {
            'default': dj_database_url.config(default='sqlite:///firetracker.sqlite')
        }
        
        # Honor the 'X-Forwarded-Proto' header for request.is_secure()
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

* Adjust settings.py params, enable admin and add south to INSTALLED_APPS