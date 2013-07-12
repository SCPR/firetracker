import os, sys, site

REMOTE_APP_ROOT = "/web/archive/apps/firetracker"
INTERP = "%s/virtualenv/firetracker/bin/python" % REMOTE_APP_ROOT

if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(REMOTE_APP_ROOT)
sys.path.append('%s/firetracker' % REMOTE_APP_ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_production'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
