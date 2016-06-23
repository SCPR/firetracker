from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from calfire_tracker.models import CalWildfire, WildfireTweet
import sys
import time
import logging
import datetime
import pytz
from twitter import *
from datetime import tzinfo, date, time, timedelta
from pytz import timezone
from dateutil import parser

logger = logging.getLogger("firetracker")

TWITTER_CONSUMER_KEY = settings.TWEEPY_CONSUMER_KEY
TWITTER_CONSUMER_SECRET = settings.TWEEPY_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN = settings.TWEEPY_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET = settings.TWEEPY_ACCESS_TOKEN_SECRET
LOCAL_TIMEZONE = pytz.timezone("US/Pacific")
TWITTER_TIMEZONE = timezone("UTC")


class TwitterHashtagResult(object):
    """
    describes and gives structure to a single tweet
    """

    def __init__(self, hashtag, text, created_at, id, screen_name, profile_image_url):
        """
        give our data some structure
        """
        self.tweet_hashtag = hashtag
        self.tweet_text = text
        self.tweet_created_at = created_at
        self.tweet_id = id
        self.tweet_screen_name = screen_name
        self.tweet_profile_image_url = profile_image_url

    def save_tweet(self, tweet):
        """
        connects to database and writes tweet instance
        """
        try:
            obj, created = WildfireTweet.objects.get_or_create(
                tweet_id=tweet.tweet_id,
                defaults={
                    "tweet_hashtag": tweet.tweet_hashtag,
                    "tweet_screen_name": tweet.tweet_screen_name.encode("ascii", "ignore"),
                    "tweet_text": tweet.tweet_text.encode("ascii", "ignore"),
                    "tweet_created_at": tweet.tweet_created_at.replace(tzinfo=utc),
                    "tweet_profile_image_url": tweet.tweet_profile_image_url,
                }
            )
        except Exception, exception:
            logger.error(exception)
            raise


class TwitterHashtagSearch(object):

    def __init__(self):
        date_object = datetime.datetime.now()
        queryset = CalWildfire.objects.filter(
            year=date_object.year).order_by("-date_time_started", "fire_name")
        for item in queryset:
            max_id = None
            search_is_done = False
            while (search_is_done == False):
                tweet_results = self.get_tweets(item.twitter_hashtag, max_id)
                self.build_tweet_from(item.twitter_hashtag, tweet_results)
                if max_id == None:
                    search_is_done = True
                else:
                    logger.debug("Retrieving more tweets since %s" % (max_id))

    def get_tweets(self, hashtag, max_id):
        """
        function to auth with twitter and return tweets
        """
        twitter_object = Twitter(
            auth=OAuth(
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_TOKEN_SECRET,
                TWITTER_CONSUMER_KEY,
                TWITTER_CONSUMER_SECRET
            )
        )
        try:
            tweet_results = twitter_object.search.tweets(
                q=hashtag,
                count=100,
                result_type="recent",
                include_entities=False,
                max_id=max_id,
                lang="en"
            )
            return tweet_results
        except TwitterHTTPError, exception:
            logger.error(exception.response_data["errors"])
            if exception.response_data["errors"][0]["code"] == 88:
                return

    def get_max_id(self, results):
        """
        get the max_id of the next twitter search if present
        """
        # see if the metadata has a next_results key
        # value is the idea to pull tweets from
        more_tweets = results["search_metadata"].has_key("next_results")
        # if there are more
        if more_tweets == True:
            # find the max id
            parsed_string = results["search_metadata"][
                "next_results"].split("&")
            parsed_string = parsed_string[0].split("?max_id=")
            max_id = parsed_string[1]
        # otherwise
        else:
            # max id is nothing
            max_id = None
        # return the max id
        return max_id

    def build_tweet_from(self, hashtag, results):
        """
        function to auth with twitter and return tweets
        """
        for tweet in results["statuses"]:
            if tweet["retweet_count"] == 0 or tweet["retweet_count"] == None:
                logger.debug("%s: %s" % (hashtag, len(results)))
                tweet_date = parser.parse(tweet["created_at"])
                tweet_date = tweet_date.replace(tzinfo=TWITTER_TIMEZONE)
                obj = TwitterHashtagResult(
                    hashtag,
                    tweet["text"].encode("ascii", "ignore"),
                    tweet_date,
                    tweet["id"],
                    tweet["user"]["screen_name"].encode("ascii", "ignore"),
                    tweet["user"]["profile_image_url"].encode(
                        "ascii", "ignore"),
                )
                obj.save_tweet(obj)

if __name__ == "__main__":
    task_run = TwitterHashtagSearch()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
