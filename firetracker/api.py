from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from wildfires.models import Wildfire

class WildfireResource(ModelResource):
    class Meta:
        queryset = Wildfire.objects.all()
        resource_name = 'wildfire'
        #fields = ['fire_name', 'county', 'acres_burned', 'containment_percent', 'date_started', 'last_update']
        allowed_methods = ['get']
        limit = 100