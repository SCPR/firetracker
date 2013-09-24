from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from calfire_tracker.models import CalWildfire, WildfireTweet
import csv, time, datetime, logging, re, types
from datetime import tzinfo, datetime, date, time, timedelta
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

class a_single_tweet():
    ''' describes and gives structure to a single tweet '''
    def __init__(self, tweet_hashtag, tweet_id, tweet_screen_name, tweet_text, tweet_created_at, tweet_profile_image_url):
        self.tweet_hashtag = tweet_hashtag
        self.tweet_id = tweet_id
        self.tweet_screen_name = tweet_screen_name
        self.tweet_text = tweet_text
        self.tweet_created_at = tweet_created_at
        self.tweet_profile_image_url = tweet_profile_image_url

def create_list_of_fire_hashtags():
    ''' pull the list of twitter hashtags from the database '''
    list_of_hashtags = []
    query_for_hashtags = CalWildfire.objects.values_list('twitter_hashtag', flat=True).order_by('-date_time_started', 'fire_name')[0:20]
    for hashtag in query_for_hashtags:
        list_of_hashtags.append(hashtag)
    search_tweepy_for_hashtags(list_of_hashtags)

def search_tweepy_for_hashtags(list_of_hashtags):
    ''' search tweepy for hashtags '''
    auth1 = tweepy.auth.OAuthHandler(settings.TWEEPY_CONSUMER_KEY, settings.TWEEPY_CONSUMER_SECRET)
    auth1.set_access_token(settings.TWEEPY_ACCESS_TOKEN, settings.TWEEPY_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth1)
    container_of_tweets = []
    delete_older_tweets_from_database()
    for hashtag in list_of_hashtags:
        update_savetime_on_wildfire(hashtag)
        for tweet in tweepy.Cursor(api.search, q=hashtag, count=10, result_type='recent', lang='en').items():
            this_single_tweet = a_single_tweet(hashtag, tweet.id, tweet.user.screen_name, tweet.text, tweet.created_at, tweet.user.profile_image_url)
            container_of_tweets.append(this_single_tweet)
        write_tweets_to_database(container_of_tweets)

def delete_older_tweets_from_database():
    ''' queries database for tweets older than 10 days and deletes '''
    startdate = date.today()
    enddate = timedelta(days=10)
    displaydate = startdate - enddate
    WildfireTweet.objects.filter(tweet_created_at__lte=displaydate).delete()

def write_tweets_to_database(container_of_tweets):
    ''' connects to database and writes tweet instance '''
    for tweet in container_of_tweets:
        try:
            obj, created = WildfireTweet.objects.get_or_create(
                tweet_id = tweet.tweet_id,
                defaults={
                    'tweet_hashtag': tweet.tweet_hashtag,
                    'tweet_id': tweet.tweet_id,
                    'tweet_screen_name': tweet.tweet_screen_name.encode('ascii', 'ignore'),
                    'tweet_text': tweet.tweet_text.encode('ascii', 'ignore'),
                    'tweet_created_at': tweet.tweet_created_at.replace(tzinfo=utc),
                    'tweet_profile_image_url': tweet.tweet_profile_image_url,
                }
            )
        except Exception, err:
            logging.debug('ERROR: %s\n' % str(err))

def update_savetime_on_wildfire(hashtag):
    query_wildfires_for_hashtag = CalWildfire.objects.filter(twitter_hashtag=hashtag)
    for wildfire in query_wildfires_for_hashtag:
        wildfire.save()