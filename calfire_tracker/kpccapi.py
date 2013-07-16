import simplejson as json
import urllib
import logging

# log everything and send to stderr
logging.basicConfig(level=logging.DEBUG)

# search assethost for an image
def search_assethost(kpcc_image_token, assethost_id):
    url_prefix = 'http://a.scpr.org/api/assets/'
    url_suffix = '.json?auth_token='
    search_url = '%s%s%s%s' % (url_prefix, assethost_id, url_suffix, kpcc_image_token)
    json_response = urllib.urlopen(search_url)
    json_response = json_response.readlines()
    js_object = json.loads(json_response[0])
    asset_url_link = js_object['urls']['full']
    asset_photo_credit = js_object['owner']
    images_dict = {'asset_url_link': asset_url_link, 'asset_photo_credit': asset_photo_credit}
    logging.debug(images_dict)
    return images_dict
if __name__ == "__main__": search_assethost()