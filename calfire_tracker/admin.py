from calfire_tracker.models import CalWildfire
from django.contrib import admin

class CalWildfireAdmin(admin.ModelAdmin):

	list_display = ('fire_name', 'date_time_started', 'injuries', 'acres_burned', 'containment_percent', 'last_updated', 'last_scraped',)

        list_per_page = 10

        ordering = ('-date_time_started',)

        date_hierarchy = 'date_time_started'

        save_on_top = True

        prepopulated_fields = {'fire_slug': ('fire_name',)}

        fieldsets = [
            ('Fire Details', {
                'fields': [
                    'fire_name',
                    'fire_slug',
                    'county',
                    'promoted_fire',
                    'twitter_hashtag',
                    'date_time_started',
                    'location',
                    'computed_location',
                    'location_latitude',
                    'location_longitude',
                    'location_geocode_error',
                    'administrative_unit',
                    'more_info',
                    'last_scraped',
                ]
            }),

            ('Basic Stats', {
                'classes': ('collapse', 'wide', 'extrapretty',),
                'fields': [
                    'last_updated',
                    'containment_percent',
                    'acres_burned',
                    'injuries',
                    'evacuations',
                    'structures_threatened',
                    'structures_destroyed',
                ]
            }),

            ('Situation On The Ground', {
                'classes': ('collapse', 'wide', 'extrapretty',),
                'fields': [
                    'phone_numbers',
                    'road_closures',
                    'cause',
                    'cooperating_agencies',
                    'conditions',
                    'notes',
                ]
            }),

            ('Resources', {
                'classes': ('collapse', 'wide', 'extrapretty',),
                'fields': [
                    'total_dozers',
                    'total_helicopters',
                    'total_fire_engines',
                    'total_fire_personnel',
                    'total_water_tenders',
                    'total_airtankers',
                    'total_fire_crews',
                ]
            }),

        ]

	list_filter = ['date_time_started', 'last_updated']
	search_fields = ['fire_name', 'county', 'acres_burned']

admin.site.register(CalWildfire, CalWildfireAdmin)