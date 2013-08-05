import re
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.management import call_command

delimiter_re = re.compile(r'[ ]+')


class Command(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True)
    command = models.TextField(_('Command'), blank=True)
    created = models.DateTimeField(_('Created'), editable=False)
    updated = models.DateTimeField(_('Updated'), editable=False)
    order = models.IntegerField(_('Command run order'), default=0)

    class Meta:
        verbose_name = _('Command')
        verbose_name_plural = _('Commands')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        self.updated = now()
        if not self.id:
            self.created = self.updated

        if not self.slug:
            self.slug = slugify(self.title)
        super(Command, self).save(**kwargs)

    def has_filled_command(self):
        return bool(self.command)

    def _prepare_command(self):
        def _parse_value(value):
            if value == "True":
                return True
            if value == "False":
                return False
            if "." in value:
                try:
                    return float(value)
                except ValueError:
                    return value
            try:
                return int(value)
            except ValueError:
                return value
        a = []
        kw = dict()
        command = self.command.strip()
        command_parts = delimiter_re.split(command)
        c = command_parts[0]
        for cp in command_parts[1:]:
            if "=" in cp:
                key, value = cp.split("=")
                kw[key] = _parse_value(value)
            else:
                a.append(cp)
        return c, a, kw

    def execute(self):
        c, a, kw = self._prepare_command()
        return call_command(c, *a, **kw)
