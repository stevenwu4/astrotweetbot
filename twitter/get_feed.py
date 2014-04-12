'''
Module to get who tweeted at @astro_tweet_bot and then tell the server stuff
'''

import os
import twitter
import re

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

class TwitterBot(object):

    def __init__(self):
       self.api = twitter.Api(consumer_key = CONSUMER_KEY,
            consumer_secret = CONSUMER_SECRET,
            access_token_key = ACCESS_TOKEN_KEY,
            access_token_secret= ACCESS_TOKEN_SECRET)
       self.POLL = 1

    def _determine_freshness(self, time):
        # determines if we are going to respond to a tweet
        # params:
        #   time: the time the tweet was sent at
        print time
        year = 
        day = re.search('[0-9].', time).group(0)
        

    def get_feed(self):
        # gets all the mentions
        mentions = self.api.GetMentions()
        for i in mentions:
            self._determine_freshness(i.created_at)

    def tweet_at(self, mssg, user_scr=None, user_id=None):
        # Tweets at a specific user
        self.api.PostDirectMessage(mssg, 
            screen_name=user_scr, 
            user_id=user_id)

    def test(self):
        self.get_feed()

if __name__ == "__main__":
    TwitterBot().test()
