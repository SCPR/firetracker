from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from calfire_tracker.models import CalWildfire

class CalWildfireResource(ModelResource):
    class Meta:
        queryset = CalWildfire.objects.all()
        resource_name = 'wildfires'
        fields = [
            'acres_burned',
            'administrative_unit',
            'air_quality_rating',
            'cause',
            'computed_location',
            'conditions',
            'containment_percent',
            'cooperating_agencies',
            'county',
            'current_situation',
            'damage_assessment',
            'date_time_started',
            'evacuations',
            'fire_name',
            'injuries',
            'last_scraped',
            'last_updated',
            'location',
            'location_latitude',
            'location_longitude',
            'more_info',
            'notes',
            'phone_numbers',
            'road_closures',
            'structures_threatened',
            'structures_destroyed',
            'total_dozers',
            'total_helicopters',
            'total_fire_engines',
            'total_fire_personnel',
            'total_water_tenders',
            'total_airtankers',
            'total_fire_crews',
            'training',
            'twitter_hashtag',
        ]
        allowed_methods = ['get']
        limit = 10