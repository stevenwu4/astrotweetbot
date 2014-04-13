'''
Module that scrapes a given website and returns astronomical data info
'''

import requests
from twit.twitter_bot import TwitterBot
# Tonight sky parser
from scraper import parser

class RequestWeb(object):
    
    def __init__(self):
        self.tb = TwitterBot()
        
    def _return_msg(self, main, msg):
        if main == "success":
            return {'error': False, 'success':True, 'msg':msg}
        else:
            return {'error': True, 'success':False, 'msg':msg}

    def determine_response(self, call, args):
        tar = args['respond_to'].strip()
        if tar == None or tar == "":
            return self._return_msg('fail', 'No target user') 

        if call == "sky":
            self.tb.tweet_at('Hey, you requested sky again', 
                user_scr=tar)
            return self._return_msg('success', 'tweeted the sky')
        
        #TODO: make satellite parser
        elif call == "satellite":
            # TODO: call the satellite scraper
            self.tb.tweet_at('Hey, you requested satellite', 
                user_scr=tar)
            return self._return_msg('success', 'tweeted the satellite')
        else:
            return self._return_msg('fail', 'unspecified query')
