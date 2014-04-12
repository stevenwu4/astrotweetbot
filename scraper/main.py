html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

from bs4 import BeautifulSoup
import urllib
import urllib2
soup = BeautifulSoup(html_doc)

# print(soup.prettify())

# response = urllib2.urlopen('http://python.org/')
# html = response.read()
# print
# print
# print html

a = """
    Asteroids	1
    Comets	1
    Conutine.x	146
    Conutine.y	17
    Date	4/12/2014
    Doubles	1
    Galaxies	1
    Globs	1
    Horizon	45
    Latitude	41.1
    Len	4
    Longitude	-75.8
    NE	1
    Nebula	1
    OpenCl	1
    Planets	1
    StarGrp	1
    Start	20
    TimeZone	b-4
"""
url = "http://tonightssky.com/BigList.php"

b = [x.strip() for x in a.split(' ')]
b = [x for x in b if x != '']
b = [x.split("\t") for x in b]
values = dict(b)

form_data = urllib.urlencode(values)
req = urllib2.Request(url, form_data)
response = urllib2.urlopen(req)
html_result = response.read()
soup = BeautifulSoup(html_result)
a = soup.find_all('table', border=0)
a = a[2]
b = a.find_all('hr')
# a = a.find_all('td')
print(repr(b))


c = b[2].find_next()
print c
print('='*20)
if len(c.find_next_siblings('tr')) == 5:
    print c.find_next_siblings('tr')[2]
print('='*20)
print repr(c.find_next('tr'))
print "block"*20

# file = open('muhahah.html', 'w')
# file.write(response.read())

