"""
	https://deb.debian.org/debian/
	https://deb.debian.org/debian-debug/
	https://deb.debian.org/debian-ports/
	https://deb.debian.org/debian-security/

	suites: oldstable, stable, testing, unstable, or experimental
"""

import json
from urllib.request import urlopen

def getSourceFileFromLink(link):
	print('Release file: ', link + '/Release')

my_ip = str(urlopen('http://ip.42.pl/raw').read(), 'utf-8')

url = 'http://freegeoip.net/json/' + my_ip

data = str(urlopen(url).read(), 'utf-8')

js = json.loads(data)
print('IP Adress: '         +   js['ip'])
print('Country Code: '      +   js['country_code'])
print('Country Name: '      +   js['country_name'])
print()

with open('/etc/apt/sources.list') as f:
	for line in f:
		if line.startswith('#') or line == '\n':
			continue

		data = line.split(' ')
		country = data[1].split('.')[0].split('//')[1]

		# print(country.upper())
		# print(js['country_code'])
		# print(country.upper() == js['country_code'])

		if country.upper() == js['country_code']:
			print('The country is fine')
		else:
			print('The mirror is bad!')

		print('Type: {0}, uri: {1}, distribution: {2}, packages: {3}'.format( ('binary package' if data[0] == 'deb' else 'source package'), data[1], data[2], [x for x in data[3:-1]] ))
		
		links = 'Package link: {0}'.format(data[1] + '/dists/' + data[2])		
		
		for component in data[3:-1]:
			source = getSourceFileFromLink('{0}/{1}'.format(data[1] + '/dists/' + data[2], component))


		if data[3:-1] == []:
			print(data)
			source = getSourceFileFromLink('{0}/{1}'.format(data[1] + '/dists', data[2]))


		print()


