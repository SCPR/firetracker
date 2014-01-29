from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.conf import settings
from calfire_tracker.models import CalWildfire, WildfireTweet
import csv, time, logging, re, types, datetime, pytz, tweepy
from datetime import tzinfo, date, time, timedelta
from pytz import timezone
from dateutil import parser
from titlecase import titlecase

logging.basicConfig(format='\033[1;36m%(levelname)s:\033[0;37m %(message)s', level=logging.DEBUG)

class Command(BaseCommand):
    help = 'Pulls tweets via Tweepy and associates with fires '
    def handle(self, *args, **options):
        create_list_of_hashtags()
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

def create_list_of_hashtags():
    ''' pull a queryset of 30 latest twitter hashtags from the database '''
    hashtag_queryset = CalWildfire.objects.values_list('twitter_hashtag', flat=True).order_by('-date_time_started', 'fire_name')[0:30]
    hashtag_list = list(hashtag_queryset)
    delete_older_tweets_from_database(25)
    for hashtag in hashtag_list:
        tweepy_search_for(hashtag)

def tweepy_search_for(hashtag):
    ''' search tweepy for hashtags '''
    auth1 = tweepy.auth.OAuthHandler(settings.TWEEPY_CONSUMER_KEY, settings.TWEEPY_CONSUMER_SECRET)
    auth1.set_access_token(settings.TWEEPY_ACCESS_TOKEN, settings.TWEEPY_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth1)
    logging.debug(hashtag)
    for tweet in tweepy.Cursor(
        api.search,
        q=hashtag,
        result_type='recent',
        lang='en').items(20):

        this_single_tweet = a_single_tweet(hashtag, tweet.id, tweet.user.screen_name, tweet.text, tweet.created_at.replace(tzinfo=pytz.UTC), tweet.user.profile_image_url)
        write_to_database(this_single_tweet)

def write_to_database(tweet):
    ''' connects to database and writes tweet instance '''
    logging.debug(tweet)
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
        update_savetime_on_wildfire(tweet.tweet_hashtag)
    except Exception, err:
        logging.debug('ERROR: %s\n' % str(err))

def delete_older_tweets_from_database(number_of_days):
    ''' queries database for tweets older than argument and deletes '''
    start_date = date.today()
    end_date = timedelta(days=number_of_days)
    display_date = start_date - end_date
    wildfire_tweets = WildfireTweet.objects.filter(tweet_created_at__lte=display_date)
    for tweet in wildfire_tweets:
        tweet.delete()

def update_savetime_on_wildfire(hashtag):
    ''' runs the save function on a given wildfire '''
    query_wildfires_for_hashtag = CalWildfire.objects.filter(twitter_hashtag=hashtag)
    for wildfire in query_wildfires_for_hashtag:
        wildfire.save()