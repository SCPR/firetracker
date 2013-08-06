from calfire_tracker.models import CalWildfire, WildfireUpdate, WildfireTweet
from django.contrib import admin

class WildfireTweetAdmin(admin.ModelAdmin):
	list_display = ('tweet_created_at', 'tweet_screen_name')
        list_per_page = 10
        search_fields = ['tweet_text']

class WildfireTweetInline(admin.StackedInline):
    model = WildfireTweet
    extra = 4

class WildfireUpdateAdmin(admin.ModelAdmin):
	list_display = ('fire_name', 'date_time_update', 'update_text', 'source',)
        list_per_page = 10
        search_fields = ['update_text']

class WildfireUpdateInline(admin.StackedInline):
    model = WildfireUpdate
    extra = 1

class CalWildfireAdmin(admin.ModelAdmin):
	list_display = ('fire_name', 'data_source', 'promoted_fire', 'asset_host_image_id', 'date_time_started', 'location_geocode_error', 'injuries', 'acres_burned', 'containment_percent', 'county', 'last_updated', 'last_scraped',)
	list_filter = ['data_source', 'county', 'date_time_started', 'last_updated']
	search_fields = ['fire_name', 'county', 'acres_burned']
        inlines = (WildfireUpdateInline, WildfireTweetInline)
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
                    'promoted_fire',
                    'asset_host_image_id',
                    'twitter_hashtag',
                    'air_quality_rating',
                    'last_scraped',
                    'data_source',
                ]
            }),
            ('General Details', {
                'fields': [
                    'fire_name',
                    'county',
                    'acres_burned',
                    'containment_percent',
                    'date_time_started',
                    'last_updated',
                    'administrative_unit',
                    'more_info',
                    'fire_slug',
                    'county_slug',
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
                ]
            }),
            ('Fire Stats', {
                'classes': ('collapse', 'wide', 'extrapretty',),
                'fields': [
                    'injuries',
                    'evacuations',
                    'structures_threatened',
                    'structures_destroyed',
                ]
            }),
            ('Resources Deployed', {
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
            ('Situation On The Ground', {
                'classes': ('collapse', 'wide', 'extrapretty',),
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
                    'notes',
                ]
            }),
        ]

        actions = [
            'featured',
            'unfeature',
        ]

        def featured(self, request, queryset):
            queryset.update(promoted_fire = True)
        featured.short_description = "Add Fire to Featured Section"

        def unfeature(self, request, queryset):
            queryset.update(promoted_fire = False)
        unfeature.short_description = "Remove Fire to Featured Section"

admin.site.register(WildfireTweet, WildfireTweetAdmin)
admin.site.register(WildfireUpdate, WildfireUpdateAdmin)
admin.site.register(CalWildfire, CalWildfireAdmin)