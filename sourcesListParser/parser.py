"""
	/debian/
	/debian-debug/
	/debian-ports/
	/debian-security/
"""

with open('/etc/apt/sources.list') as f:
	for line in f:
		if line.startswith('#') or line == '\n':
			continue

		data = line.split(' ')
		print('Type: {0}, uri: {1}, distribution: {2}, packages: {3}'.format( ('binary package' if data[0] == 'deb' else 'source package'), data[1], data[2], [x for x in data[3:-1]] ))
		print('Package link: {0}'.format(data[1] + '/dists/' + data[2]))
		print()