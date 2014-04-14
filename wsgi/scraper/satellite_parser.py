from datetime import datetime
from bs4 import BeautifulSoup, SoupStrainer
import urllib, urllib2

#import os

SATELLITE_FLYBYS_URL = 'http://www.spaceweather.com/flybys/flybys.php'
"""
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_REVERSE_GEOCODE_URL = (
    'https://maps.googleapis.com/maps/api/geocode/json'
    '?latlng={lat},{long}'
    '&sensor=true'
    '&result_type=postal_code'
    '&key={api_key}'
)
"""

def get_satellite_tweet(inbound_json):
    #latitude = inbound_json['lat']
    #longitude = inbound_json['long']
    zip_code = inbound_json['zip_code']
    payload = {
        'zip': zip_code
    }
    payload = urllib.urlencode(payload)

    request = urllib2.Request(SATELLITE_FLYBYS_URL, payload)
    response = urllib2.urlopen(request)
    html_result = response.read()

    soup = BeautifulSoup(html_result)
    tables = soup.find_all('table', background='images/flyover_tablebg.jpg')
    
    this_month = datetime.now().strftime('%B')
    this_day = str(datetime.now().day)
    today = this_month + ' ' + this_day

    todays_table_index = 0
    #Find out which table is today's
    for i, table in enumerate(tables):
        row = table.find('tr')
        tds = row.find_all('td')
        for td in tds:
            if td.text.strip() == today:
                todays_table_index = i

    todays_table = tables[todays_table_index]
    


if __name__ == '__main__':
    get_satellite_tweet({'zip_code': '55441'})
