import gevent
from gevent import Timeout
from gevent.subprocess import Popen, PIPE
import re

timeout_seconds = 1
package_count = 5

all_threads = []
data = {}

def parse_result(some_string):
	"""
	EXAMPLE:

		PING 216.58.212.35 (216.58.212.35) 56(84) bytes of data.
		64 bytes from 216.58.212.35: icmp_seq=1 ttl=57 time=21.7 ms
		64 bytes from 216.58.212.35: icmp_seq=2 ttl=57 time=1.22 ms

		--- 216.58.212.35 ping statistics ---
		2 packets transmitted, 2 received, 0% packet loss, time 1001ms
		rtt min/avg/max/mdev = 1.229/11.501/21.773/10.272 ms

	"""

	packet_loss_group = re.search(r"(?<=received, )[0-9]+", some_string)
	packet_loss = packet_loss_group.group(0)

	rtt_group = re.search(r"(?<=mdev = )\d+\.\d+/\d+\.\d+/\d+\.\d+/\d+\.\d+", some_string)
	try:
		values_arr = rtt_group.group(0).split("/")
	except Exception as e:
		#Total loss of pings..
		return 100, "N/A", "N/A" 

	rtt_avg = float(values_arr[1])
	mdev = float(values_arr[3])

	return packet_loss, rtt_avg, mdev

def ping(ip, number_of_packages, current_order, timeout):
	#print('ping -i {0} -q -W {1} -c {2} {3}'.format(timeout/number_of_packages, timeout, number_of_packages, ip))
	sub = Popen(['ping -i {0} -q -W {1} -c {2} {3}'.format(timeout/number_of_packages, timeout, number_of_packages, ip)], stdout=PIPE, shell=True)
	out, err = sub.communicate()
	data[current_order] = [ip, out]


with open("test_Data/ips", "r") as f:
	for current_order, current_ip in enumerate(f):
		g = gevent.spawn(ping, ip = current_ip, number_of_packages = package_count, current_order = current_order, timeout = timeout_seconds)
		all_threads.append(g)

gevent.joinall(all_threads)

for key, value in data.items():
	packet_loss, rtt_avg, mdev = parse_result(str(value[1], "utf-8"))
	print("IP order {0}; IP: {1}; packet_loss: {2}; rtt: {3}; mdev: {4}".format(key, value[0].strip(), packet_loss, rtt_avg, mdev))
