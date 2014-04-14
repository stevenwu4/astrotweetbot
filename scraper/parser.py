"""
Usage:
    parser.py parser (--filename=<filename>)
    parser.py get_html_page (--filename=<filename)
"""

from docopt import docopt
from bs4 import BeautifulSoup, SoupStrainer
import json
import urllib, urllib2


TONIGHTSSKY_URL = 'http://tonightssky.com/BigList.php'

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
    : 'Caelum',
    : 'Camelopardalis',
    : 'Cancer',
    : 'Canes Venatici',
    : 'Canis Major',
    : 'Canis Minor',
    : 'Capricornus',
    : 'Carina',
    : 'Cassiopeia',
    : 'Centaurus',
    : 'Cepheus',
    : 'Cetus',
    : 'Chamaeleon',
    : 'Circinus',
    : 'Columba',
    : 'Coma Berenices',
    : 'Corona Australis',
    : 'Corona Borealis',
    : 'Corvus',
    : 'Crater',
    : 'Crux',
    : 'Cygnus',
    : 'Delphinus',
    : 'Dorado',
    : 'Draco',
    : 'Equuleus',
    : 'Eridanus',
    : 'Fornax',
    : 'Gemini',
    : 'Grus',
    : 'Hercules',
    : 'Horologium',
    : 'Hydra',
    : 'Hydrus',
    : 'Indus',
    : 'Lacerta',
    : 'Leo',
    : 'Leo Minor',
    : 'Lepus',
    : 'Libra',
    : 'Lupus',
    : 'Lynx',
    : 'Lyra',
    : 'Mensa',
    : 'Microscopium',
    : 'Monoceros',
    : 'Musca',
    : 'Norma',
    : 'Octans',
    : 'Ophiuchus',
    : 'Orion',
    : 'Pavo',
    : 'Pegasus',
    : 'Perseus',
    : 'Phoenix',
    : 'Pictor',
    : 'Pisces',
    : 'Piscis Austrinus',
    : 'Puppis',
    : 'Pyxis',
    : 'Reticulum',
    : 'Sagitta',
    : 'Sagittarius',
    : 'Scorpius',
    : 'Sculptor',
    : 'Scutum',
    : 'Serpens',
    : 'Sextans',
    : 'Taurus',
    : 'Telescopium',
    : 'Triangulum',
    : 'Triangulum Australe',
    : 'Tucana',
    : 'Ursa Major',
    : 'Ursa Minor',
    : 'Vela',
    : 'Virgo',
    : 'Volans',
    : 'Vulpecula',
}


def get_html_page(name_of_html):
    payload = urllib.urlencode({
        'Asteroids': '1',
        'Comets': '1',
        'Conutine.x': '146',
        'Conutine.y': '17',
        'Date': '12/14/2013',
        'Doubles': '1',
        'Galaxies': '1',
        'Globs': '1',
        'Horizon': '45',
        'Latitude': '49.1',
        'Len': '4',
        'Longitude': '-78.8',
        'NE': '1',
        'Nebula': '1',
        'OpenCl': '1',
        'Planets': '1',
        'StarGrp': '1',
        'Start': '20',
        'TimeZone': 'b-4'
    })

    request = urllib2.Request(TONIGHTSSKY_URL, payload)
    response = urllib2.urlopen(request)
    html_result = response.read()

    destination_html = open(name_of_html, 'w')
    destination_html.write(html_result)


def scrape_html(html):
    filter_only_form = SoupStrainer('form')
    soup = BeautifulSoup(
        open(html), parse_only=filter_only_form
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
            'constellation': constellation,
        }

        print json.dumps(row_header_mapping, indent=4, separators=(',', ': '))
        print next_row_is_pair

        list_of_mappings.append(row_header_mapping)
        #print i, ':', len(all_cells_in_row)

    #for mapping in list_of_mappings:
    #    print json.dumps(mapping, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    args = docopt(__doc__)
    filename = args['--filename']
    run_parser = args['parser']
    run_get_html = args['get_html_page']

    if run_parser:
        scrape_html(filename)
    if run_get_html:
        get_html_page(filename)

    #get_html_page(filename)
