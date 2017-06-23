"""
	https://deb.debian.org/debian/
	https://deb.debian.org/debian-debug/
	https://deb.debian.org/debian-ports/
	https://deb.debian.org/debian-security/

	suites: oldstable, stable, testing, unstable, or experimental
"""

import json, re, sys, pycountry, gevent

from gevent import monkey
monkey.patch_all()

from urllib.request import urlopen
from urllib.error import HTTPError as fetchError

godRepoToLevel = {
	'normal': 'https://deb.debian.org/debian',
	'debug': 'https://deb.debian.org/debian-debug',
#	'ports': 'https://deb.debian.org/debian-ports',
	'ports': 'http://ftp.debian.org/debian',
	'security': 'https://deb.debian.org/debian-security',
}

def getGodRepo(distro):
	if 'backports' in distro:
		return godRepoToLevel['ports']
	elif '/updates' in distro:
		return godRepoToLevel['security']
	else:
		return godRepoToLevel['normal']

def getReleaseFileFromLink(link):
	fileURL = link + '/Release'
	file = str(urlopen(fileURL).read(), 'utf-8').split('\n')
	return file

def getDateLineFromFile(file):
	for line in file:
		if line.startswith('Date'):
			return line

def getCountryCodeByGeoPosition():
	my_ip = str(urlopen('http://ip.42.pl/raw').read(), 'utf-8')
	url = 'http://freegeoip.net/json/' + my_ip
	data = str(urlopen(url).read(), 'utf-8')
	js = json.loads(data)
	return js['country_code']	

def isInGoodCountry(data):
	myCountryCode = getCountryCodeByGeoPosition()

	country = data[1].split('//')[1]
	components = country.split('.')
	for component in components:
		component = component.upper()
		for country in pycountry.countries:
			if component == country.alpha_2:
				if component == myCountryCode:
					return 1
				else:
					return -1
	return 0

def makeIt(line):
	data = line.split(' ')
	godBaseLink = getGodRepo(data[2])
	components = data[3:-1]

	try:

		source = getReleaseFileFromLink('{0}'.format(data[1] + '/dists/' + data[2]))
		sourceTestAgainst = getReleaseFileFromLink('{0}/dists/{1}'.format(godBaseLink, data[2]))

	except fetchError as e:
		print(data[1] + '/dists/' + data[2], '-1')
	else:
		dateSource = getDateLineFromFile(source)
		dateSourceTestAgainst = getDateLineFromFile(sourceTestAgainst)
		print(data[1] + '/dists/' + data[2], '1' if dateSource == dateSourceTestAgainst else '0', isInGoodCountry(data))




allThreads = []
with open('/etc/apt/sources.list') as f:
	for line in f:
		if line.startswith('#') or line == '\n':
			continue
		
		allThreads.append(gevent.spawn(makeIt, line))

gevent.joinall(allThreads)
