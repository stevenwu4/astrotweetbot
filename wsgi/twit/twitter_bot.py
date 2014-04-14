'''
Module to get who tweeted at @astro_tweet_bot and then tell the server stuff
Expected twitter request:
    For sky
    @astro_tweet_bot, sky, <start_time> + <length> [, <difficulty>, <info wantedone>;<info wantedtwo>]
    For satellite
    @astro_tweet_bot,  satellite, <postal_code>
'''

import os
from twitter import (
    Api,
    TwitterError)
import time
import requests

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

class TwitterBot(object):

    def __init__(self):
        self.api = Api(consumer_key = CONSUMER_KEY,
            consumer_secret = CONSUMER_SECRET,
            access_token_key = ACCESS_TOKEN_KEY,
            access_token_secret= ACCESS_TOKEN_SECRET)
        # cron is minutely
        self.POLL = 1
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
   
    # GETS THE FEED FROM TWITTER AND SENDS PAYLOAD TO API
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
                    
    def get_position(self, res):
        pos = {'lat':None, 'long':None}

        # gets the place tag
        if res.place:
            sum_lat = 0
            sum_long = 0
            box = res.place.get('bounding_box').get('coordinates')[0]
            for i in box:
                sum_lat += i[0]
                sum_long += i[1]
            pos['lat'] = (sum_lat/4.0)
            pos['long'] = (sum_long/4.0)

        # gets the geo tag
        if res.coordinates:
            pos['lat'] = res.coordinates.get('coordinates')[0]
            pos['long'] = res.coordinates.get('coordinates')[1]
        
        return pos

    def send_payload_tonightsky(self, res):
        payload = {
            'lat': None,
            'long': None,
            'when': None,
            'length': None,
            'difficulty': 1,
            'features': 'Globular Clusters;Open Clusters;Nebula;Galaxies;Planets;Comets;Asteroids;Double Stars;Star Group'
        }
        pos = self.get_position(res)
        payload['lat'] = pos['lat']
        payload['long'] = pos['long']
        # fills in the rest of the payload
        queries = res.text.split(',')

        tar_time = queries[2].split('+')
        if len(tar_time) == 2:
            payload['when'] = tar_time[0].strip()
            payload['length'] = tar_time[1].strip()
        
        if len(queries) > 3:
            payload['difficulty'] = queries[3].strip()
        if len(queries) > 4:
            payload['features'] = queries[4].strip()


        if payload['lat'] == None or payload['long'] == None or payload['when'] == None or payload['length'] == None:
            print 'invalid'
            return

        name = res.user.screen_name
        url = ('http://bot-astrotweet.rhcloud.com/api/v1/sky?respond_to=' + 
        name + "&lat=" + str(payload['lat']) +
        "&long=" + str(payload['long']) + 
        "&when=" + str(payload['when']) +
        "&length=" + str(payload['length'])+
        "&difficulty=" + str(payload['difficulty']) +
        "&features=" + str(payload['features']))
        print url
        if (requests.get(url)):
            print 'sent tweet'

    def send_payload_satellite(self, res):
        payload = {'lat':None, 'long':None, 'postal_code':None}
        pos = self.get_position(res)
        payload['lat'] = pos['lat']
        payload['long'] = pos['long']
        payload['postal_code'] = res.text.split(',')[-1].encode().strip()
       
        name = res.user.screen_name
        url = ('http://bot-astrotweet.rhcloud.com/api/v1/satellite?respond_to=' + name + '&lat=' + str(payload['lat']) + "&long=" + str(payload['long']) + "&postal_code=" + payload['postal_code'])
        print url
#        if (requests.get(url)):
#            print 'sent tweet'
        print payload

    def tweet_at(self, mssg, user_scr):
        # Tweets at a specific user
        res = "@" + user_scr + " " + mssg + " " + time.strftime('%h/%d/ %H:%M')
        try:
            self.api.PostUpdate(res)
        except TwitterError:
            print 'TwitterError'
            pass

    def test(self):
        self.get_feed()

if __name__ == "__main__":
    TwitterBot().test()
