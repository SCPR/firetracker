from csvimporter.models import CSV
from django.contrib import admin

class CSVAdmin(admin.ModelAdmin):

    list_display = ()

admin.site.register(CSV, CSVAdmin)