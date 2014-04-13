'''
Module that scrapes a given website and returns astronomical data info
'''

import requests
from twit.twitter_bot import TwitterBot

success = {
    'success': True,
    'error': False
}
fail = {
    'success':False,
    'error':True,
}

class RequestWeb(object):
    
    def __init__(self):
        print 'creating twitter bot'
        self.tb = TwitterBot()
        
    def _return_msg(self, main, msg):
        res = main
        res['msg'] = msg
        return res

    def determine_response(self, call, args):
        print 'getting response'
        tar = args['respond_to']
        if tar == None:
            return self._return_msg(fail, 'No target user') 

        if call == "sky":
            # TODO: call the sky scraper
            self.tb.api.PostDirectMessage('Hey, you requested sky again', 
                screen_name=tar)
            return self._return_msg(success, 'tweeted the sky')
        elif call == "satellite":
            # TODO: call the satellite scraper
            self.tb.api.PostDirectMessage('Hey, you requested satellite', 
                screen_name=tar)
            return self._return_msg(success, 'tweeted the satellite')
        else:
            return self._return_msg(fail, 'unspecified query')
