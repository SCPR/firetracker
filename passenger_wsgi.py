import os, sys, site, yaml

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_production")

sys.path.append(os.getcwd())

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
