# -*- coding: utf-8 -*-
'''
Module for scraping info from tonight sky
'''

from bs4 import BeautifulSoup, SoupStrainer
import json
import urllib, urllib2


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


def get_html_page(name_of_html, inbound_json):
    payload = {}

    #Load the user variables that don't require logic
    latitude = inbound_json['lat']
    longitude = inbound_json['long']
    start = inbound_json['when']
    length = inbound_json['length']
    #Load the difficulty settings
    #eg: if user said 3, it maps to small scope
    #We assume that a user specifying a difficulty
    #is comfortable with the levels below the specified level
    difficulty = int(inbound_json['difficulty'])
    for i in range(difficulty):
        difficulty_payload_key = DIFFICULTY_KEYS[i]
        payload[difficulty_payload_key] = '1'
    #Load the desired object types
    


    payload = {
        #Location data from geotagged tweet
        'Latitude': '49.1',#
        'Longitude': '-78.8',#
        'Horizon': '45',
        #When to observe
        #*GMT Timezone, tweets come in GMT
        'Start': '20',#
        'Len': '4',#
        'TimeZone': 'A0',
        'Date': '12/14/2013',#
        #Difficulty of observing
        #'NE': '1',
        #'Bino': '1',
        #'Small': '1',
        #'Easy': '1',
        #'Medium': '1',
        #'Hard': '1',
        #What to observe
        'Globs': '1',#
        'OpenCl': '1',#
        'Nebula': '1',#
        'Galaxies': '1',#
        'Planets': '1',#
        'Comets': '1',#
        'Asteroids': '1',#
        'Doubles': '1',#
        'StarGrp': '1',#
        #Never get prompted about having too many results
        'BigOK.x': '83',
        'BigOK.y': '13',
        'BigOK': 'Yes'
        #No idea what these are for, but we need 'em
        'Conutine.x': '146',#
        'Conutine.y': '17',#
    }
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
            'primary_catalog': primary_catalog,
            'object_description': object_desc,
            'magnitude': magnitude,
            'constellation': CONSTELLATION_MAPPING[constellation],
        }

        print json.dumps(row_header_mapping, indent=4, separators=(',', ': '))
        print next_row_is_pair

        list_of_mappings.append(row_header_mapping)
        #print i, ':', len(all_cells_in_row)

    #for mapping in list_of_mappings:
    #    print json.dumps(mapping, indent=4, separators=(',', ': '))
    return list_of_mappings
