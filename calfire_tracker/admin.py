from calfire_tracker.models import CalWildfire, WildfireUpdate, WildfireTweet
from django.contrib import admin
from django.utils.timezone import utc, localtime
import time, datetime, logging
from datetime import tzinfo
import pytz
from pytz import timezone

class WildfireTweetAdmin(admin.ModelAdmin):
	list_display = ('tweet_screen_name', 'tweet_hashtag', 'tweet_created_at', 'tweet_text')
        list_per_page = 10
        search_fields = ['tweet_text']

class WildfireUpdateAdmin(admin.ModelAdmin):
	list_display = ('fire_name', 'date_time_update', 'update_text', 'source',)
        list_per_page = 10
        search_fields = ['update_text']

class WildfireUpdateInline(admin.StackedInline):
    model = WildfireUpdate
    extra = 1

class CalWildfireAdmin(admin.ModelAdmin):
	list_display = ('fire_name', 'update_lockout', 'promoted_fire', 'asset_host_image_id', 'data_source', 'date_time_started', 'location_geocode_error', 'injuries', 'acres_burned', 'containment_percent', 'county', 'last_updated', 'last_scraped', 'notes', 'last_saved',)
	list_filter = ['data_source', 'county', 'date_time_started', 'last_updated']
	search_fields = ['fire_name', 'county', 'acres_burned']
        inlines = (WildfireUpdateInline,)
        list_per_page = 10
        ordering = ('-date_time_started',)
        date_hierarchy = 'date_time_started'
        save_on_top = True
        prepopulated_fields = {
            'fire_slug': ('fire_name',),
            'county_slug': ('county',)
        }
        fieldsets = [
            ('Management & Curation', {
                'fields': [
                    'update_lockout',
                    'promoted_fire',
                    'asset_host_image_id',
                    'fire_name',
                    'county',
                    'acres_burned',
                    'containment_percent',
                    'date_time_started',
                    'twitter_hashtag',
                    'air_quality_rating',
                    'year',
                    'fire_slug',
                    'county_slug',
                    'created_fire_id',
                    'last_updated',
                    'last_scraped',
                    'historical_narrative',
                    'notes',
                ]
            }),
            ('Fire Stats', {
                'classes': ('wide', 'extrapretty',),
                'fields': [
                    'injuries',
                    'evacuations',
                    'structures_threatened',
                    'structures_destroyed',
                    'administrative_unit',
                    'data_source',
                    'more_info',
                ]
            }),
            ('Location Information', {
                'classes': ('collapse', 'wide', 'extrapretty',),
                'fields': [
                    'location',
                    'computed_location',
                    'location_latitude',
                    'location_longitude',
                    'location_geocode_error',
                    'perimeters_image',
                ]
            }),
            ('Image Resources', {
                'classes': ('collapse', 'wide', 'extrapretty',),
                'fields': [
                    'asset_url_link',
                    'asset_photo_credit',
                ]
            }),
            ('Resources Deployed', {
                'classes': ('wide', 'extrapretty',),
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
            ('Situation On The Ground', {
                'classes': ('wide', 'extrapretty',),
                'fields': [
                    'cause',
                    'cooperating_agencies',
                    'road_closures',
                    'school_closures',
                    'conditions',
                    'current_situation',
                    'damage_assessment',
                    'training',
                    'phone_numbers',
                ]
            })
        ]

        actions = [
            'featured',
            'unfeature',
            'lock_fire_data',
            'unlock_fire_data',
            'update_last_saved_time_and_image',
        ]

        def update_last_saved_time_and_image(self, request, queryset):
            date = datetime.datetime.now()
            queryset.update(last_saved = date)
            for object in queryset:
                object.save()
        update_last_saved_time_and_image.short_description = "Update Last Saved and Image"

        def featured(self, request, queryset):
            queryset.update(promoted_fire = True)
        featured.short_description = "Add Fire to Featured Section"

        def unfeature(self, request, queryset):
            queryset.update(promoted_fire = False)
        unfeature.short_description = "Remove Fire to Featured Section"

        def lock_fire_data(self, request, queryset):
            queryset.update(update_lockout = True)
        lock_fire_data.short_description = "Lock From Auto Updates"

        def unlock_fire_data(self, request, queryset):
            queryset.update(update_lockout = False)
        unlock_fire_data.short_description = "Allow Auto Updates"

admin.site.register(WildfireTweet, WildfireTweetAdmin)
admin.site.register(WildfireUpdate, WildfireUpdateAdmin)
admin.site.register(CalWildfire, CalWildfireAdmin)