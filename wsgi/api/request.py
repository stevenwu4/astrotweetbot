'''
Module that scrapes a given website and returns astronomical data info
'''

import requests
from twit.twitter_bot import TwitterBot

class RequestWeb(object):
    
    def __init__(self):
        self.tb = TwitterBot()
        
    def _return_msg(self, main, msg):
        if main == "success":
            res = {'error': False, 'success':True, 'msg':msg}
        else:
            res = {'error': True, 'success':False, 'msg':msg}
        return res

    def determine_response(self, call, args):
        tar = args['respond_to']
        if tar == None:
#            return self._return_msg('fail', 'No target user') 
            return

        if call == "sky":
            # TODO: call the sky scraper
            self.tb.tweet_at('Hey, you requested sky again', 
                user_scr=tar)
#            return self._return_msg('success', 'tweeted the sky')
        elif call == "satellite":
            # TODO: call the satellite scraper
            self.tb.tweet_at('Hey, you requested satellite', 
                user_scr=tar)
#            return self._return_msg('success', 'tweeted the satellite')
#        else:
 #           return self._return_msg('fail', 'unspecified query')
