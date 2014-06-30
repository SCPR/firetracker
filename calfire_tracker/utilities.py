from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from geopy import geocoders
import pytz, time, datetime, requests, logging

logging.basicConfig(format='\033[1;36m%(levelname)s:\033[0;37m %(message)s', level=logging.DEBUG)

def search_assethost_for_image(kpcc_image_token, **kwargs):
    ''' model save function to query kpcc image api given an asset_host_id '''
    if kwargs['image_id'] is not None:
        url_prefix = 'http://a.scpr.org/api/assets/'
        url_suffix = '.json?auth_token='
        search_url = '%s%s%s%s' % (url_prefix, kwargs['image_id'], url_suffix, kpcc_image_token)
        kpcc_query_api = requests.get(search_url, headers={"From": "ckeller@scpr.org","User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19"})
        kpcc_image_asset = kpcc_query_api.json()
        try:
            kpcc_image_data = {'asset_url_link': kpcc_image_asset['urls']['full'], 'asset_photo_credit': kpcc_image_asset['owner'], 'asset_host_image_id': kwargs['image_id']}
        except:
            kpcc_image_data = {'asset_url_link': None, 'asset_photo_credit': None, 'asset_host_image_id': None}
    else:
        kpcc_image_data = {'asset_url_link': None, 'asset_photo_credit': None, 'asset_host_image_id': None}
    return kpcc_image_data


def fill_air_quality_data(location_latitude, location_longitude):
    try:
        air_quality_url = 'http://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude=%s&longitude=%s&distance=30&API_KEY=AABE5F75-6C5A-47C2-AB74-2D138C9055B2' % (location_latitude, location_longitude)
        air_quality_query = requests.get(air_quality_url, headers= {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19"})
        air_quality_json = air_quality_query.json()
        if len(air_quality_json) == 0:
            air_quality_rating = None
            air_quality_parameter = None
        elif len(air_quality_json) >= 1:
            for data in air_quality_json:
                if data["ParameterName"] == "PM2.5":
                    air_quality_rating = data["AQI"]
                    air_quality_parameter = "Fine particles (PM2.5)"
                elif data["ParameterName"] == "O3":
                    air_quality_rating = data["AQI"]
                    air_quality_parameter = "Ozone (O3)"
                else:
                    air_quality_rating = None
                    air_quality_parameter = None
        else:
            air_quality_rating = None
            air_quality_parameter = None
    except:
        air_quality_rating = None
        air_quality_parameter = None
        print "exception for %s, %s\n" % (location_latitude, location_longitude)
    return {"air_quality_rating": air_quality_rating, "air_quality_parameter": air_quality_parameter}


def fill_geocode_data(computed_location):
    if computed_location is not None:
        try:
            g = geocoders.GoogleV3()
            address = smart_str(computed_location)
            computed_location, (location_latitude, location_longitude) = g.geocode(address)
            geolocation_data = {
                'computed_location': str(computed_location),
                'location_latitude': location_latitude,
                'location_longitude': location_longitude,
                'location_geocode_error': False,
            }
        except (UnboundLocalError, ValueError,geocoders.google.GQueryError):
            geolocation_data = {
                'computed_location': str(computed_location),
                'location_latitude': None,
                'location_longitude': None,
                'location_geocode_error': True,
            }
        return geolocation_data