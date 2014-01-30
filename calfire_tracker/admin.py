from calfire_tracker.models import CalWildfire, WildfireUpdate, WildfireTweet, WildfireAnnualReview, WildfireDisplayContent
from django.conf import settings
from django.contrib import admin
from django.utils.timezone import utc, localtime
import time, datetime, logging, requests, tweepy
from datetime import tzinfo
import pytz
from pytz import timezone

logging.basicConfig(format='\033[1;36m%(levelname)s:\033[0;37m %(message)s', level=logging.DEBUG)

class WildfireAnnualReviewAdmin(admin.ModelAdmin):
	list_display = ('year', 'acres_burned', 'number_of_fires', 'jurisdiction', 'last_saved')
        list_per_page = 10
        search_fields = ['year', 'acres_burned', 'number_of_fires', 'administrative_unit']
    	list_filter = ['year', 'acres_burned', 'number_of_fires', 'administrative_unit']
        ordering = ('-year', 'administrative_unit')

class WildfireDisplayContentAdmin(admin.ModelAdmin):
    list_display = ('content_headline', 'content_link', 'content_type', 'last_saved',)
    list_per_page = 10
    search_fields = ['content_headline']
    list_filter = ['resource_content_type', 'display_content_type']

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
	list_display = ('fire_name', 'update_lockout', 'promoted_fire', 'asset_host_image_id', 'data_source', 'date_time_started', 'location_geocode_error', 'injuries', 'acres_burned', 'containment_percent', 'air_quality_rating', 'county', 'last_updated', 'last_scraped', 'notes', 'last_saved',)
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
            'update_air_quality_data',
            #'tweet_fire_details_from_admin',
        ]

        def tweet_fire_details_from_admin(self, request, queryset):
            auth1 = tweepy.auth.OAuthHandler(settings.TWEEPY_CONSUMER_KEY, settings.TWEEPY_CONSUMER_SECRET)
            auth1.set_access_token(settings.TWEEPY_ACCESS_TOKEN, settings.TWEEPY_ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth1)
            for object in queryset:
                tweet_text = '%s is at %s%% containment. View details on @KPCC\'s FireTracker: http://projects.scpr.org/firetracker/%s/' % (object.twitter_hashtag, object.containment_percent, object.fire_slug)
                logging.debug(tweet_text)
                api.update_status(tweet_text)
        tweet_fire_details_from_admin.short_description = "Tweet details of the selected fire"

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

        def update_last_saved_time_and_image(self, request, queryset):
            date = datetime.datetime.now()
            queryset.update(last_saved = date)
            for object in queryset:
                object.save()
        update_last_saved_time_and_image.short_description = "Update Last Saved and Image"

        def update_air_quality_data(self, request, queryset):
            for object in queryset:
                object.save()
        update_air_quality_data.short_description = "Update Air Quality"

admin.site.register(CalWildfire, CalWildfireAdmin)
admin.site.register(WildfireTweet, WildfireTweetAdmin)
admin.site.register(WildfireUpdate, WildfireUpdateAdmin)
admin.site.register(WildfireAnnualReview, WildfireAnnualReviewAdmin)
admin.site.register(WildfireDisplayContent, WildfireDisplayContentAdmin)