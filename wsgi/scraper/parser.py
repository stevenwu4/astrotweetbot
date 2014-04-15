# -*- coding: utf-8 -*-
'''
Module for scraping info from tonight sky
'''

from scraped_to_tweet import (
    tonightssky_info_to_tweet, satellite_info_to_tweet
)
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import json
import urllib, urllib2
import re

#TONIGHTS SKY CONSTANTS
TONIGHTSSKY_URL = 'http://tonightssky.com/BigList.php'
GOOGLE_TIMEZONE_API_KEY = 'AIzaSyDcHQQkaxRFKS4l2xMJaJ4YTo-nO53SwWM'
#http://dibonsmith.com/constel.htm
#Acronyms taken from clicking the constellation & finding it in url
CONSTELLATION_MAPPING = {
    'And': 'Andromeda',
    'Ant': 'Antlia',
    'Aps': 'Apus',
    'Aqr': 'Aquarius',
    'Aql': 'Aquila',
    'Ara': 'Ara',
    'Ari': 'Aries',
    'Aur': 'Auriga',
    'Boo': 'Boötes',
    'Cae': 'Caelum',
    'Cam': 'Camelopardalis',
    'Cnc': 'Cancer',
    'Cvn': 'Canes Venatici',
    'Cma': 'Canis Major',
    'Cmi': 'Canis Minor',
    'Cap': 'Capricornus',
    'Car': 'Carina',
    'Cas': 'Cassiopeia',
    'Cen': 'Centaurus',
    'Cep': 'Cepheus',
    'Cet': 'Cetus',
    'Cha': 'Chamaeleon',
    'Cir': 'Circinus',
    'Col': 'Columba',
    'Com': 'Coma Berenices',
    'Cra': 'Corona Australis',
    'Crb': 'Corona Borealis',
    'Crv': 'Corvus',
    'Crt': 'Crater',
    'Cru': 'Crux',
    'Cyg': 'Cygnus',
    'Del': 'Delphinus',
    'Dor': 'Dorado',
    'Dra': 'Draco',
    'Equ': 'Equuleus',
    'Eri': 'Eridanus',
    'For': 'Fornax',
    'Gem': 'Gemini',
    'Gru': 'Grus',
    'Her': 'Hercules',
    'Hor': 'Horologium',
    'Hya': 'Hydra',
    'Hyi': 'Hydrus',
    'Ind': 'Indus',
    'Lac': 'Lacerta',
    'Leo': 'Leo',
    'Lmi': 'Leo Minor',
    'Lep': 'Lepus',
    'Lib': 'Libra',
    'Lup': 'Lupus',
    'Lyn': 'Lynx',
    'Lyr': 'Lyra',
    'Men': 'Mensa',
    'Mic': 'Microscopium',
    'Mon': 'Monoceros',
    'Mus': 'Musca',
    'Nor': 'Norma',
    'Oct': 'Octans',
    'Oph': 'Ophiuchus',
    'Ori': 'Orion',
    'Pav': 'Pavo',
    'Peg': 'Pegasus',
    'Per': 'Perseus',
    'Phe': 'Phoenix',
    'Pic': 'Pictor',
    'Psc': 'Pisces',
    'Psa': 'Piscis Austrinus',
    'Pup': 'Puppis',
    'Pyx': 'Pyxis',
    'Ret': 'Reticulum',
    'Sge': 'Sagitta',
    'Sgr': 'Sagittarius',
    'Sco': 'Scorpius',
    'Scl': 'Sculptor',
    'Sct': 'Scutum',
    'Ser': 'Serpens',
    'Sex': 'Sextans',
    'Tau': 'Taurus',
    'Tel': 'Telescopium',
    'Tri': 'Triangulum',
    'Tra': 'Triangulum Australe',
    'Tuc': 'Tucana',
    'Uma': 'Ursa Major',
    'Umi': 'Ursa Minor',
    'Vel': 'Vela',
    'Vir': 'Virgo',
    'Vol': 'Volans',
    'Vul': 'Vulpecula'
}
DIFFICULTY_KEYS = [
    'NE', 'Bino', 'Small', 'Easy', 'Medium', 'Hard'
]
FEATURE_MAPPING = {
    'Globular Clusters': 'Globs',
    'Open Clusters': 'OpenCl',
    'Nebula': 'Nebula',
    'Galaxies': 'Galaxies',
    'Planets': 'Planets',
    'Comets': 'Comets',
    'Asteroids': 'Asteroids',
    'Double Stars': 'Doubles',
    'Star Group': 'StarGrp'
}

########
#SATELLITE CONSTANTS
NUM_HEADERS_IN_SATELLITE_TABLE = 6
SATELLITE_FLYBYS_URL = 'http://www.spaceweather.com/flybys/flybys.php'
DEGREE_REGEX = re.compile('[\d]*')


def get_tonights_sky_tweet(inbound_json):
    payload = {
        #Location data from geotagged tweet
        #'Latitude': '49.1',#
        #'Longitude': '-78.8',#
        'Horizon': '45',
        #When to observe
        #*GMT Timezone, tweets come in GMT Timezone (A0)
        #'Start': '20',#
        #'Len': '4',#
        'TimeZone': 'A0',
        'Date': '{d.month}/{d.day}/{d.year}'.format(d=datetime.now()),
        #Difficulty of observing
        #'NE': '1',
        #'Bino': '1',
        #'Small': '1',
        #'Easy': '1',
        #'Medium': '1',
        #'Hard': '1',
        #What to observe
        #'Globs': '1',#
        #'OpenCl': '1',#
        #'Nebula': '1',#
        #'Galaxies': '1',#
        #'Planets': '1',#
        #'Comets': '1',#
        #'Asteroids': '1',#
        #'Doubles': '1',#
        #'StarGrp': '1',#
        #Never get prompted about having too many results
        'BigOK.x': '83',
        'BigOK.y': '13',
        'BigOK': 'Yes',
        #No idea what these are for, but we need 'em
        'Conutine.x': '146',#
        'Conutine.y': '17',#
    }
    #Load the user variables that don't require logic
    payload['Latitude'] = inbound_json['lat'].encode()
    payload['Longitude'] = inbound_json['long'].encode()
    payload['Start'] = inbound_json['when'].encode()
    payload['Len'] = inbound_json['length'].encode()
    #Load the difficulty settings
    #eg: if user said 3, it maps to small scope
    #We assume that a user specifying a difficulty
    #is comfortable with the levels below the specified level
    difficulty = int(inbound_json['difficulty'])
    for i in range(difficulty):
        difficulty_key = DIFFICULTY_KEYS[i]
        payload[difficulty_key] = '1'
    #Load the desired object types
    #['Globular Clusters', 'Open Clusters', 'Nebula', 'Galaxies'
    #'Planets', 'Comets', 'Asteroids', 'Double Stars', 'Star Group']
    list_of_features = inbound_json['features']
    for feature in list_of_features:
        feature_key = FEATURE_MAPPING[feature]
        payload[feature_key] = '1'

    payload = urllib.urlencode(payload)
    request = urllib2.Request(TONIGHTSSKY_URL, payload)
    response = urllib2.urlopen(request)
    html_result = response.read()
    filter_only_form = SoupStrainer('form')
    soup = BeautifulSoup(
        html_result, parse_only=filter_only_form
    )
    table = soup.find_all('table')
    info_table = table[0]
    #^ type Tag
    """
    all_cells = info_table.find_all('td')
    print len(all_cells)
    for i, cell in enumerate(all_cells):
        print i, ':', cell
        print '\n'

    print '='*20
    #Delete unnecessary instruct span text and
    #Header cells
    all_cells = all_cells[12:]
    
    for i, cell in enumerate(all_cells):
        print i, ':', cell.text.strip()
        print '\n'
    """

    all_rows = info_table.find_all('tr')
    #print len(all_rows)

    #First 3 rows are garbage; description, headers & <hr>'s
    all_rows = all_rows[3:]
    #print all_rows

    next_row_is_pair = False

    list_of_mappings = []
    for i, row in enumerate(all_rows):
        row_header_mapping = {}

        all_cells_in_row = row.find_all('td')
        #We'll skip every row that has only one cell, because
        #those only contain <hr>'s        
        if len(all_cells_in_row) <= 1 or next_row_is_pair:
            next_row_is_pair = False
            continue
        #For each row, will need to check the 10th cell
        #because it will have an indicator for if the 
        #next row is a pair to this row
        try:
            tenth_cell = all_cells_in_row[9]
            try:
                if tenth_cell['rowspan'] > 1:
                    next_row_is_pair = True
            except KeyError:
                pass
        except IndexError as e:
            pass
        primary_catalog = all_cells_in_row[1].text.strip()
        object_desc = all_cells_in_row[3].text.strip()
        magnitude = all_cells_in_row[4].text.strip()
        constellation = all_cells_in_row[7].text.strip()

        if next_row_is_pair:
            next_row = all_rows[i+1]
        
            all_cells_in_next_row = next_row.find_all('td')

            primary_catalog += ',{0}'.format(all_cells_in_next_row[1].text.strip())
            #object_desc += ',{0}'.format(all_cells_in_next_row[2].text.strip())
            #^no longer including, too much noise & not useful

        row_header_mapping = {
            'primary_catalog': primary_catalog.lstrip(','),
            'object_description': object_desc,
            'magnitude': magnitude,
            'constellation': CONSTELLATION_MAPPING[constellation.capitalize()],
        }

        #print json.dumps(row_header_mapping, indent=4, separators=(',', ': '))
        #print next_row_is_pair

        list_of_mappings.append(row_header_mapping)
        #print i, ':', len(all_cells_in_row)

    for mapping in list_of_mappings:
        print json.dumps(mapping, indent=4, separators=(',', ': '))
    
    user_name_length = len(inbound_json['user'])
    tweet = tonightssky_info_to_tweet(list_of_mappings, user_name_length)
    return tweet


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
    exit_out = False
    for i, table in enumerate(tables):
        row = table.find('tr')
        tds = row.find_all('td')
        for td in tds:
            if td.text.strip() == today:
                todays_table_index = i
                exit_out = True
        if exit_out:
            break

    todays_table = tables[todays_table_index]

    rows = todays_table.find_all('tr')
    """
    #Need to traverse backwards because for some reason,
    #the information is repeated and since we don't know at run-time
    #how many useful rows there will be, we'll traverse backwards
    #until we get the header texts
    #Some rows contain td's with no classes
    rows_stopping_index = 0
    for i, row in enumerate(reversed(rows))
        tds = row.find_all('td')
        for td in tds:
            try:
                if td['class'] == 'spacecraftColumnTitleText':
                    rows_stopping_index = i
                    break
            except:
                pass
    """
    all_tds = rows[0].find_all('td')
    #Dump all useful data into a list
    list_of_info = []
    for t in tds:
        try:
            if 'satTableDataText' in t['class']:
                list_of_info.append(t.text.strip())
        except:
            pass
    #Find out how many rows in the table there were
    if len(list_of_info)%NUM_HEADERS_IN_SATELLITE_TABLE != 0:
        return (
            'Sorry, there was an error getting the data.'
            'Here is a cookie for finding an error for us to debug!'
        )
    else:
        num_rows = len(list_of_info) / NUM_HEADERS_IN_SATELLITE_TABLE
    #Dump useful data into a list of dicts, each row being a dict
    list_of_mappings = []
    for i in range(num_rows):
        satellite_mapping = {}
        adjusted_index = NUM_HEADERS_IN_SATELLITE_TABLE*i
        satellite_mapping['name'] = list_of_info[adjusted_index]
        satellite_mapping['rise_time'] = list_of_info[1+adjusted_index]
        satellite_mapping['direction'] = list_of_info[2+adjusted_index]
        satellite_mapping['best_time'] = list_of_info[3+adjusted_index]
        satellite_mapping['max_elevation'] = re.search(DEGREE_REGEX, list_of_info[4+adjusted_index]).group()
        satellite_mapping['magnitude'] = list_of_info[5+adjusted_index].replace(' (dim)', '')
        list_of_mappings.append(satellite_mapping)

    for mapping in list_of_mappings:
        print json.dumps(mapping, indent=4, separators=(',', ': '))

    user_name_length = len(inbound_json['user'])
    tweet = satellite_info_to_tweet(list_of_mappings, user_name_length)
    print tweet
    return tweet
