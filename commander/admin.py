from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from commander.models import Command

import logging
logger = logging.getLogger(__name__)


class CommandAdmin(admin.ModelAdmin):
    list_display = ('title', 'command', 'created', 'updated', "order")
    search_fields = ['title', 'command']
    prepopulated_fields = {'slug': ('title',)}
    actions = tuple(list(admin.ModelAdmin.actions) + ['run_commands'])

    def run_commands(self, request, queryset):
        qs = queryset.order_by("order")
        count_wanted = qs.count()
        count_executed = count_wanted
        for c in qs:
            if c.has_filled_command():
                try:
                    c.execute()
                except Exception, e:
                    logger.error("Command executed from admin failed", exc_info=True)
                    self.message_user(request, _("Comand %(title)s faild, %(error)s") % {"title": c.title,
                                                                                         "error": e})
                    count_executed -= 1
            else:
                count_executed -= 1
                logger.warning("Command %s is empty", c.slug)
        self.message_user(request, _("%(ce)s commands from %(cw)s was successfully executed") % {"ce": count_executed,
                                                                                                 "cw": count_wanted})
    run_commands.short_description = _("Run commands")


admin.site.register(Command, CommandAdmin)
