'''
Module to get who tweeted at @astro_tweet_bot and then tell the server stuff
Expected twitter request:
    For sky
    @astro_tweet_bot, sky, <start_time> + <length> [, <difficulty>, <info wanted>]
    For satellite
    @astro_tweet_bot,  satellite, <postal_code>
'''

import os
import twitter
import time

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
        self.POLL = 100
        self.data_sources_key = ['sky', 'satellite']

    def _determine_freshness(self, tm):
        # determines if we are going to respond to a tweet
        # params:
        #   time: the time the tweet was sent at
        year = tm[-4:]
        if time.strftime('%Y') != year:
            return False
        
        month = tm[4:7]
        if time.strftime('%h') != month:
            return False
           
        day = tm[8:10]
        # greater than because of server offset
        if int(time.strftime('%d')) > int(day):
            return False

        hour = tm[11:13]
        # offset hour b/c of servers
        if (int(time.strftime('%H'))+4)%24 != int(hour):
            return False

        mnt = tm[14:16]
        if int(time.strftime('%M')) > (int(mnt)+self.POLL):
            return False
        
        return True
    
    def get_feed(self):
        # gets all the mentions
        mentions = self.api.GetMentions()
        for i in mentions:
            # makes sure it is not an onld tweet   
            if self._determine_freshness(i.created_at):
                print i.created_at
                # checks what kind of info they want
                if self.get_type(i.text) == 'sky':
                    self.send_payload_tonightsky(i)
                elif self.get_type(i.text) == 'satellite':
                    self.send_payload_satellite(i)

    def get_type(self, text):
        queries = text.split(',')
        if len(queries) < 3:
            return False
        else:
            for i in queries:
                if i.strip() in self.data_sources_key:
                    return i.strip()
        return False
                    

    def send_payload_tonightsky(self, res):
        payload = {
            'lat': None,
            'long': None,
            'when': None,
            'length': None,
            'difficulty': 1,
            'features': ['Globular Clusters', 'Open Clusters',
                'Nedula', 'Galaxies', 'Planets', 'Comets',
                'Asteroids', 'Double Stars', 'Star Group']
        }
        # gets the place tag
        if res.place:
            sum_lat = 0
            sum_long = 0
            box = res.place.get('bounding_box').get('coordinates')[0]
            for i in box:
                sum_lat += i[0]
                sum_long += i[1]
            payload['lat'] = (sum_lat/4.0)
            payload['long'] = (sum_long/4.0)

        # gets the geo tag
        if res.coordinates:
            payload['lat'] = res.coordinates.get('coordinates')[0]
            payload['long'] = res.coordinates.get('coordinates')[1]
        # fills in the rest of the payload
        queries = res.text.split(',')

        tar_time = queries[2].split('+')
        if len(tar_time) == 2:
            payload['when'] = tar_time[0].strip()
            payload['length'] = tar_time[1].strip()
        
        if len(queries) > 3:
            payload['difficulty'] = queries[3].strip()
        if len(queries) > 4:
            payload['features'] = queries[4].split('+')

        print payload

    def send_payload_satellite(self, res):
        payload = {'postal_code':None}

    def tweet_at(self, mssg, user_scr=None, user_id=None):
        # Tweets at a specific user
        self.api.PostDirectMessage(mssg, 
            screen_name=user_scr, 
            user_id=user_id)

    def test(self):
        self.get_feed()

if __name__ == "__main__":
    TwitterBot().test()
