#!/usr/bin/env python
import os
import sys
import newrelic.agent

if __name__ == "__main__":
    newrelic.agent.initialize("config/newrelic.ini")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_production")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
