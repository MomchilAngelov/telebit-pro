import sys, gevent, socket

def should_block(resolver):
	if resolver.CURRENT_IN_GETHOSTBYNAME_EX > resolver.OPENED_HOSTS_MAX:
			resolver.SHOULD_ACCEPT_MORE_HOSTS = 0
	if resolver.CURRENT_IN_GETHOSTBYNAME_EX < resolver.OPENED_HOSTS_MAX:
		resolver.SHOULD_ACCEPT_MORE_HOSTS = 1

	while not resolver.SHOULD_ACCEPT_MORE_HOSTS:
		gevent.sleep(2)
		if resolver.CURRENT_IN_GETHOSTBYNAME_EX > resolver.OPENED_HOSTS_MAX:
			SHOULD_ACCEPT_MORE_HOSTS = 0
		if resolver.CURRENT_IN_GETHOSTBYNAME_EX < resolver.OPENED_HOSTS_MAX:
			resolver.SHOULD_ACCEPT_MORE_HOSTS = 1


class Resolver():

	def __init__(self, outputter, class_of_pinger, should_resolve):
		self.iterations = 0
		self.threads = []
		self.outputter = outputter
		self.class_of_pinger = class_of_pinger
		self.should_resolve = should_resolve

		self.SHOULD_ACCEPT_MORE_HOSTS = 1
		self.CURRENT_IN_GETHOSTBYNAME_EX = 0

		self.OPENED_HOSTS_MAX = 800

	def isGoodIPv4(self, s):
		pieces = s.split('.')
		if len(pieces) != 4: 
			return False	
		try: 
			return all(0<=int(p)<256 for p in pieces)
		except ValueError:
			return False

	def normalizeInputForHostname(self, hostname):

		hostname = hostname.replace("https://", "", 1)
		hostname = hostname.replace("http://", "", 1)
		if hostname[-1] == "/":
			hostname = hostname[:-1]
		return hostname	

	def resolveDomainName(self, hostname, array_with_data):
		hostname = self.normalizeInputForHostname(hostname)

		should_block(self)
		self.CURRENT_IN_GETHOSTBYNAME_EX += 1

		try:
			ips = socket.gethostbyname_ex(hostname)[2]
		except Exception as e:
			ips=[hostname]

		self.CURRENT_IN_GETHOSTBYNAME_EX -= 1

		for ip in ips:
			array_with_data['ip'] = ip
			self.ping(array_with_data)
			self.iterations += 1

	def ping(self, item):
		pinger = self.class_of_pinger(item = item)
		self.threads.append(gevent.spawn(pinger.ping, self.outputter))

	def ping_all(self, items):
		if self.should_resolve:
			for item in items:
				self.threads.append(gevent.spawn(self.resolveDomainName, item['address'], item))
		else:
			for item in items:
				self.ping(item)

		gevent.joinall(self.threads)
