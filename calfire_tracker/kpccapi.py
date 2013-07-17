import simplejson as json
import urllib

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
<<<<<<< HEAD
    return images_dict

class kpcc_api_article():
    def __init__(self, permalink, image_asset, publish_date, short_title):
        self.permalink = permalink
        self.image_asset = image_asset
        self.publish_date = publish_date
        self.short_title = short_title

# search kpcc api for related articles to display on detail pages
def search_kpcc_article_api(query_params, query_limit):
    url_prefix = 'http://www.scpr.org/api/v2/content/?'
    url_types = 'types=news,blogs,segments'
    url_query = '&query=%s' % (query_params)
    url_limit = '&limit=%d' % (query_limit)
    url_page = '&page=1'
    search_url = '%s%s%s%s%s' % (url_prefix, url_types, url_query, url_limit, url_page)
    json_response = urllib.urlopen(search_url)
    json_response = json_response.readlines()
    js_object = json.loads(json_response[0])
    articles = []
    for kpcc_article in js_object:
        article_permalink = kpcc_article['permalink']

        try:
            article_image_asset = kpcc_article['assets'][0]['small']['url']
        except:
            article_image_asset = 'http://projects.scpr.org/firetracker/static/media/archive-fire-photo-fallback.jpg'

        article_publish_date = kpcc_article['published_at']
        article_short_title = kpcc_article['short_title']
        this_article = kpcc_api_article(article_permalink, article_image_asset, article_publish_date, article_short_title)
        articles.append(this_article)
    return articles

if __name__ == "__main__": search_kpcc_article_api()
=======
    return images_dict
>>>>>>> parent of 4f2af3e... adds class to create a kpcc article -- my first attempt at using a class -- and function to query kpcc article api
