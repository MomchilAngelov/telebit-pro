import socket

def get_ips_for_host(host):
	try:
		ips = socket.gethostbyname_ex(host)
	except socket.gaierror:
		ips=[]
	return ips

ips = get_ips_for_host('www.google.com')
print(repr(ips[2]))