import os, sys, site, yaml

env = os.environ.setdefault("DJANGO_ENV", "production")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_%s" % env)

app_config = yaml.load(open("config/app.yml", 'r'))[env]

INTERP = os.path.join(app_config['bin_root'], 'python')

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
