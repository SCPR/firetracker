from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from calfire_tracker.models import CalWildfire

class CalWildfireResource(ModelResource):
    class Meta:
        queryset = CalWildfire.objects.all()
        resource_name = 'wildfires'
        #fields = ['fire_name', 'county', 'acres_burned', 'containment_percent', 'date_started', 'last_update']
        allowed_methods = ['get']
        limit = 100