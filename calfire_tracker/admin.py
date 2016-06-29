from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.utils.timezone import utc, localtime
from calfire_tracker.models import CalWildfire, AltCreateWildfire, WildfireUpdate, WildfireTweet, WildfireAnnualReview, WildfireDisplayContent
import time
import datetime
import logging
import requests
import tweepy
from datetime import tzinfo
import pytz
from pytz import timezone

logger = logging.getLogger("firetracker")

class WildfireAnnualReviewAdmin(admin.ModelAdmin):
    list_display = (
        "year",
        "acres_burned",
        "number_of_fires",
        "jurisdiction",
        "last_saved",
    )
    list_per_page = 10
    search_fields = (
        "year",
        "acres_burned",
        "number_of_fires",
        "administrative_unit",
    )
    list_filter = (
        "year",
        "acres_burned",
        "number_of_fires",
        "administrative_unit",
    )
    ordering = (
        "-year",
        "administrative_unit",
    )


class WildfireDisplayContentAdmin(admin.ModelAdmin):
    list_display = (
        "content_headline",
        "content_link",
        "resource_content_type",
        "display_content_type",
        "last_saved",
    )
    list_per_page = 10
    search_fields = (
        "content_headline",
    )
    list_filter = (
        "resource_content_type",
        "display_content_type",
    )


class WildfireTweetAdmin(admin.ModelAdmin):
    list_display = (
        "tweet_screen_name",
        "tweet_hashtag",
        "tweet_created_at",
        "tweet_text",
    )
    list_per_page = 10
    search_fields = (
        "tweet_text",
    )


class WildfireUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "fire_name",
        "date_time_update",
        "update_text",
        "source",
    )
    list_per_page = 10
    search_fields = (
        "update_text",
    )


class WildfireUpdateInline(admin.StackedInline):
    model = WildfireUpdate
    extra = 1


class CalWildfireAdmin(admin.ModelAdmin):

    def queryset(self, request):
        qs = super(CalWildfireAdmin, self).queryset(request)
        return qs

    list_display = (
        "fire_name",
        "fire_closeout_toggle",
        "update_lockout",
        "promoted_fire",
        "asset_host_image_id",
        "county",
        "date_time_started",
        "acres_burned",
        "containment_percent",
        "more_info",
        "last_updated",
        "last_scraped",
        "last_saved",
    )

    list_filter = (
        "date_time_started",
        "data_source",
        "county",
        "last_updated",
    )

    list_editable = (
        "acres_burned",
        "containment_percent",
    )

    search_fields = (
        "fire_name",
        "county",
        "acres_burned",
    )

    preserve_filters = True

    inlines = (WildfireUpdateInline,)

    list_per_page = 20

    ordering = (
        "containment_percent",
        "-date_time_started",
    )

    date_hierarchy = "date_time_started"

    save_on_top = True

    prepopulated_fields = {
        "county_slug": ("county",),
        "fire_slug": ("fire_name",)
    }

    fieldsets = [
        ("Management & Curation", {
            "fields": [
                "fire_closeout_toggle",
                "update_lockout",
                "promoted_fire",
                "asset_host_image_id",
                "fire_name",
                "county",
                "acres_burned",
                "containment_percent",
                "date_time_started",
                "twitter_hashtag",
                "air_quality_rating",
                "air_quality_parameter",
                "year",
                "last_updated",
                "historical_narrative",
                "notes",
            ]
        }),
        ("Fire Stats", {
            "classes": (
                "wide",
                "extrapretty",
            ),
            "fields": [
                "injuries",
                "evacuations",
                "structures_threatened",
                "structures_destroyed",
                "administrative_unit",
                "data_source",
                "more_info",
            ]
        }),
        ("MetaData", {
            "classes": (
                "collapse",
                "wide",
                "extrapretty",
            ),
            "fields": [
                "fire_slug",
                "county_slug",
                "created_fire_id",
                "last_scraped",
            ]
        }),
        ("Location Information", {
            "classes": (
                "collapse",
                "wide",
                "extrapretty",
            ),
            "fields": [
                "location",
                "computed_location",
                "location_latitude",
                "location_longitude",
                "location_geocode_error",
                "perimeters_image",
            ]
        }),
        ("Image Resources", {
            "classes": (
                "collapse",
                "wide",
                "extrapretty",
            ),
            "fields": [
                "asset_url_link",
                "asset_photo_credit",
            ]
        }),
        ("Resources Deployed", {
            "classes": (
                "wide",
                "extrapretty",
            ),
            "fields": [
                "total_dozers",
                "total_helicopters",
                "total_fire_engines",
                "total_fire_personnel",
                "total_water_tenders",
                "total_airtankers",
                "total_fire_crews",
            ]
        }),
        ("Situation On The Ground", {
            "classes": (
                "wide",
                "extrapretty",
            ),
            "fields": [
                "cause",
                "cooperating_agencies",
                "road_closures",
                "school_closures",
                "conditions",
                "current_situation",
                "damage_assessment",
                "training",
                "phone_numbers",
            ]
        })
    ]

    actions = [
        "featured",
        "unfeature",
        "lock_fire_data",
        "unlock_fire_data",
        "close_fire",
        "unclose_fire",
        "update_last_saved_time_and_image",
        "update_air_quality_data",
        #"tweet_fire_details_from_admin",
    ]

    def save_model(self, request, obj, form, change):
        if not obj.fire_name:
            messages.error(request, "You can't create a fire without a name")
            save_this = False

        if not obj.county:
            messages.error(request, "You can't create a fire without a county")
            save_this = False

        if not obj.fire_slug:
            obj.fire_slug = "%s-%s-%s" % (slugify(obj.fire_name), slugify(obj.county), obj.year)

        if obj.location == "" or obj.location == None:
            messages.error(request, "Hey there's no display location. Do we know where this fire is?")
            save_this = False

        if obj.location_geocode_error == True:
            messages.info(request, "Did you look for latitude & longitude data for this fire")
            save_this = True

        if obj.acres_burned == "" or obj.acres_burned == None:
            messages.error(request, "This fire needs a valid figure for acres burned")
            save_this = False

        if not obj.date_time_started:
            messages.error(request, "This fire needs a valid start date and time")
            save_this = False

        if "computed_location" in form.changed_data and obj.location_geocode_error == True:
            messages.error(request, "Failed to geocode this fire's location. Please correct or remove the data in the computed location field.")
            obj.computed_location = None
            obj.location_geocode_error = True
            save_this = True

        if len(form.changed_data) > 0:
            obj.last_updated = datetime.datetime.now()
            save_this = True

        if save_this == False:
            pass
        else:
            super(CalWildfireAdmin, self).save_model(request, obj, form, change)


    def tweet_fire_details_from_admin(self, request, queryset):
        auth1 = tweepy.auth.OAuthHandler(
            settings.TWEEPY_CONSUMER_KEY, settings.TWEEPY_CONSUMER_SECRET)
        auth1.set_access_token(settings.TWEEPY_ACCESS_TOKEN,
                               settings.TWEEPY_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth1)
        for object in queryset:
            tweet_text = "%s is at %s%% containment. View details on @KPCC\'s FireTracker: http://firetracker.scpr.org/%s/" % (
                object.twitter_hashtag, object.containment_percent, object.fire_slug)
            logging.debug(tweet_text)
            api.update_status(tweet_text)
    tweet_fire_details_from_admin.short_description = "Tweet details of the selected fire"

    def featured(self, request, queryset):
        queryset.update(promoted_fire=True)
    featured.short_description = "Add Fire to Featured Section"

    def unfeature(self, request, queryset):
        queryset.update(promoted_fire=False)
    unfeature.short_description = "Remove Fire to Featured Section"

    def lock_fire_data(self, request, queryset):
        queryset.update(update_lockout=True)
    lock_fire_data.short_description = "Lock From Auto Updates"

    def unlock_fire_data(self, request, queryset):
        queryset.update(update_lockout=False)
    unlock_fire_data.short_description = "Allow Auto Updates"

    def close_fire(self, request, queryset):
        queryset.update(fire_closeout_toggle=True)
        queryset.update(update_lockout=True)
    close_fire.short_description = "Close Out & Lock This Fire"

    def unclose_fire(self, request, queryset):
        queryset.update(fire_closeout_toggle=False)
    unclose_fire.short_description = "Unclose This Fire"

    def update_last_saved_time_and_image(self, request, queryset):
        date = datetime.datetime.now()
        queryset.update(last_saved=date)
        for object in queryset:
            object.save()
    update_last_saved_time_and_image.short_description = "Update Last Saved and Image"

    def update_air_quality_data(self, request, queryset):
        for object in queryset:
            object.save()
    update_air_quality_data.short_description = "Update Air Quality"

class AltCreateWildfireAdmin(admin.ModelAdmin):

    def queryset(self, request):
        qs = super(AltCreateWildfireAdmin, self).queryset(request)
        return qs

    list_display = (
        "fire_name",
        "fire_closeout_toggle",
        "update_lockout",
        "promoted_fire",
        "asset_host_image_id",
        "county",
        "date_time_started",
        "acres_burned",
        "containment_percent",
        "more_info",
        "last_updated",
    )

    list_filter = (
        "date_time_started",
        "data_source",
        "county",
        "last_updated",
    )

    list_editable = (
        "acres_burned",
        "containment_percent",
    )

    search_fields = (
        "fire_name",
        "county",
        "acres_burned",
    )

    preserve_filters = True

    inlines = (WildfireUpdateInline,)

    list_per_page = 20

    ordering = (
        "containment_percent",
        "-date_time_started",
    )

    date_hierarchy = "date_time_started"

    save_on_top = True

    prepopulated_fields = {
        "county_slug": ("county",),
        "fire_slug": ("fire_name",)
    }

    fieldsets = [

        ("Fields Needed To Create A Wildfire", {
            "description": "<p><em>This is the minimum information we need to create a new wildfire that will be displayed on Fire Tracker</em></p>",
            "classes": (
                "extrapretty",
            ),
            "fields": (
                ("fire_closeout_toggle","update_lockout","promoted_fire",),
                ("acres_burned", "containment_percent", "twitter_hashtag",),
                ("fire_name", "county",),
                "date_time_started",
                "last_updated",
                "location",
                ("administrative_unit", "data_source",),
                "more_info",
                "notes",
            )
        }),

        ("Want To Add An Image?", {
            "classes": (
                "wide",
                "extrapretty",
            ),
            "fields": [
                "asset_host_image_id",
                "asset_url_link",
                "asset_photo_credit",
                # "perimeters_image",
            ]
        }),

        ("Information About The Fire Location", {
            "classes": (
                "wide",
                "extrapretty",
            ),
            "fields": (
                "location_geocode_error",
                "computed_location",
                ("location_latitude", "location_longitude",),
            )
        }),

        ("What Can We Communicate To The Public?", {
            "classes": (
                "wide",
                "extrapretty",
            ),
            "fields": (
                ("structures_threatened", "structures_destroyed"),
                ("injuries"),
                "evacuations",
                "road_closures",
                "school_closures",
                "phone_numbers",
                "air_quality_rating",
                "air_quality_parameter",
            )
        }),

        ("Resources Deployed", {
            "classes": (
                "wide",
                "extrapretty",
                "collapse",
            ),
            "fields": (
                ("total_fire_personnel",
                "total_fire_crews",
                "total_fire_engines",
                "total_dozers",),
                ("total_helicopters",
                "total_water_tenders",
                "total_airtankers",),
            )
        }),

        ("Situation On The Ground", {
            "classes": (
                "wide",
                "extrapretty",
                "collapse",
            ),
            "fields": (
                "historical_narrative",
                "cooperating_agencies",
                "cause",
                "conditions",
                "current_situation",
                "damage_assessment",
                "training",
            )
        }),

        ("Behind The Scenes Data", {
            "classes": (
                "extrapretty",
                "collapse",
            ),
            "fields": (
                ("fire_slug", "county_slug",),
                ("created_fire_id", "year",),
                "last_scraped",
            )
        }),
    ]

    actions = [
        "featured",
        "unfeature",
        "lock_fire_data",
        "unlock_fire_data",
        "close_fire",
        "unclose_fire",
        "update_last_saved_time_and_image",
        "update_air_quality_data",
        #"tweet_fire_details_from_admin",
    ]

    def save_model(self, request, obj, form, change):
        if not obj.fire_name:
            messages.error(request, "You can't create a fire without a name")
            save_this = False

        if not obj.county:
            messages.error(request, "You can't create a fire without a county")
            save_this = False

        if not obj.fire_slug:
            obj.fire_slug = "%s-%s-%s" % (slugify(obj.fire_name), slugify(obj.county), obj.year)

        if obj.location == "" or obj.location == None:
            messages.error(request, "Hey there's no display location. Do we know where this fire is?")
            save_this = False

        if obj.location_geocode_error == True:
            messages.info(request, "Did you look for latitude & longitude data for this fire")
            save_this = True

        if obj.acres_burned == "" or obj.acres_burned == None:
            messages.error(request, "This fire needs a valid figure for acres burned")
            save_this = False

        if not obj.date_time_started:
            messages.error(request, "This fire needs a valid start date and time")
            save_this = False

        if "computed_location" in form.changed_data and obj.location_geocode_error == True:
            messages.error(request, "Failed to geocode this fire's location. Please correct or remove the data in the computed location field.")
            obj.computed_location = None
            obj.location_geocode_error = True
            save_this = True

        if len(form.changed_data) > 0:
            obj.last_updated = datetime.datetime.now()
            save_this = True

        if save_this == False:
            pass
        else:
            super(AltCreateWildfireAdmin, self).save_model(request, obj, form, change)

    def featured(self, request, queryset):
        queryset.update(promoted_fire=True)
    featured.short_description = "Add Fire to Featured Section"

    def unfeature(self, request, queryset):
        queryset.update(promoted_fire=False)
    unfeature.short_description = "Remove Fire to Featured Section"

    def lock_fire_data(self, request, queryset):
        queryset.update(update_lockout=True)
    lock_fire_data.short_description = "Lock From Auto Updates"

    def unlock_fire_data(self, request, queryset):
        queryset.update(update_lockout=False)
    unlock_fire_data.short_description = "Allow Auto Updates"

    def close_fire(self, request, queryset):
        queryset.update(fire_closeout_toggle=True)
        queryset.update(update_lockout=True)
    close_fire.short_description = "Close Out & Lock This Fire"

    def unclose_fire(self, request, queryset):
        queryset.update(fire_closeout_toggle=False)
    unclose_fire.short_description = "Unclose This Fire"

    def update_last_saved_time_and_image(self, request, queryset):
        date = datetime.datetime.now()
        queryset.update(last_saved=date)
        for object in queryset:
            object.save()
    update_last_saved_time_and_image.short_description = "Update Last Saved and Image"

    def update_air_quality_data(self, request, queryset):
        for object in queryset:
            object.save()
    update_air_quality_data.short_description = "Update Air Quality"


admin.site.register(CalWildfire, CalWildfireAdmin)
admin.site.register(AltCreateWildfire, AltCreateWildfireAdmin)
admin.site.register(WildfireTweet, WildfireTweetAdmin)
admin.site.register(WildfireUpdate, WildfireUpdateAdmin)
admin.site.register(WildfireAnnualReview, WildfireAnnualReviewAdmin)
admin.site.register(WildfireDisplayContent, WildfireDisplayContentAdmin)
