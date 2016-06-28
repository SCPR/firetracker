from django.contrib import admin
from django.contrib import messages
import logging

logger = logging.getLogger("firetracker")


def collect_messages(request):
    this = messages.get_messages(request)
    display_messages = {}
    display_messages["info"] = [ m for m in this if "info" in m.tags]
    display_messages["error"] = [ m for m in this if "error" in m.tags]
    display_messages["warning"] = [ m for m in this if "warning" in m.tags]
    return {"display_messages": display_messages}
