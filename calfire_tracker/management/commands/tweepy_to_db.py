from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from calfire_tracker.models import CalWildfire, WildfireTweet
import csv, time, datetime, logging, re, types
from datetime import tzinfo
import pytz
from pytz import timezone
from dateutil import parser
from titlecase import titlecase
from django.conf import settings
import tweepy

logging.basicConfig(level=logging.DEBUG)

class Command(BaseCommand):
    help = 'Pulls tweets via Tweepy and associates with fires '
    def handle(self, *args, **options):
        create_list_of_fire_hashtags()
        self.stdout.write('\nFinished Saving Tweets To Database at %s\n' % str(datetime.datetime.now()))

def create_list_of_fire_hashtags():
    ''' pull the list of twitter hashtags from the database '''
    list_of_hashtags = []
    query_for_hashtags = CalWildfire.objects.values_list('twitter_hashtag', flat=True)
    for hashtag in query_for_hashtags:
        list_of_hashtags.append(hashtag)
    save_tweets_from_hashtag_to_db(list_of_hashtags)

def save_tweets_from_hashtag_to_db(list_of_hashtags):
    ''' search tweepy for hashtags and save to db '''
    auth1 = tweepy.auth.OAuthHandler(settings.TWEEPY_CONSUMER_KEY, settings.TWEEPY_CONSUMER_SECRET)
    auth1.set_access_token(settings.TWEEPY_ACCESS_TOKEN, settings.TWEEPY_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth1)
    for hashtag in list_of_hashtags[0:3]:
        logging.debug(hashtag)
        try:
            result_list = api.search(hashtag)
        except:
            result_list = None
        if result_list is not None:
            for result in result_list:
                obj, created = WildfireTweet.objects.get_or_create(
                    tweet_id = result.id,
                    defaults={
                        'tweet_hashtag': hashtag,
                        'tweet_id': result.id,
                        'tweet_screen_name': result.user.screen_name,
                        'tweet_text': result.text,
                        'tweet_created_at': result.created_at,
                        'tweet_profile_image_url': result.user.profile_image_url,
                    }
                )
        else:
            pass