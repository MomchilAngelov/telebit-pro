import gevent
from gevent import monkey
monkey.patch_all()
from scapy.all import *

ips = [
	"104.43.195.251",
	"23.100.122.175",
	"23.96.52.53",
	"104.40.211.35",
	"191.239.213.197",
	"172.217.17.174",
	"172.217.17.164",
	"17.178.96.59",
	"17.172.224.47",
	"17.142.160.59",
	"216.58.212.2",
	"172.217.17.164",
	"31.13.91.36",
	"206.190.36.45",
	"98.139.183.24",
	"98.138.253.109",
	"216.58.206.174"
]


def stuff(timeout, inter, dst):
	sr(IP(dst=dst)/ICMP(), timeout = timeout, inter = inter)

gvent_those = [gevent.spawn(stuff, timeout = 2, inter = 0.1, dst = k) for k in ips]
gevent.joinall(gvent_those)