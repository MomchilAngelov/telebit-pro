import gevent
from gevent import Timeout
from gevent.subprocess import Popen, PIPE
import re, time, json

timeout_seconds = 1
package_count = 5

all_threads = []
data = {}
output_json = {}

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
		return 100, "N/A", "N/A" 

	rtt_avg = float(values_arr[1])
	mdev = float(values_arr[3])

	return packet_loss, rtt_avg, mdev

def ping(ip, number_of_packages, current_order, timeout):
	#print('ping -i {0} -q -W {1} -c {2} {3}'.format(timeout/number_of_packages, timeout, number_of_packages, ip))
	sub = Popen(["ping -i {0} -q -W {1} -c {2} {3}"
		.format(timeout/number_of_packages, timeout, number_of_packages, ip)], stdout=PIPE, shell=True)
	out, err = sub.communicate()
	data[current_order] = [ip, out, time.time()]


with open("test_Data/ips", "r") as f:
	for current_order, current_ip in enumerate(f):
		g = gevent.spawn(ping, ip = current_ip, number_of_packages = package_count, current_order = current_order, timeout = timeout_seconds)
		all_threads.append(g)

gevent.joinall(all_threads)

output_json["version"] = "3.0"
output_json["applications"] = {}
output_json["applications"]["icmp_pings"] = {}
output_json["applications"]["icmp_pings"]["name"] = "IMCP pings"
output_json["applications"]["icmp_pings"]["items"] = {}
items = output_json["applications"]["icmp_pings"]["items"]

for key, value in data.items():
	packet_loss, rtt_avg, mdev = parse_result(value[1].decode())
	
	items[value[0].strip()+".rtt"] = {}
	items[value[0].strip()+".rtt"]["value"] = rtt_avg
	items[value[0].strip()+".rtt"]["units"] = "ms"
	items[value[0].strip()+".rtt"]["name"] = "[{0}] ICMP ping: packet round trip time".format(value[0].strip())
	items[value[0].strip()+".rtt"]["type"] = "float"
	items[value[0].strip()+".rtt"]["timestamp"] = int(value[2])


	items[value[0].strip()+".packet_loss"] = {}
	items[value[0].strip()+".packet_loss"]["value"] = packet_loss
	items[value[0].strip()+".packet_loss"]["units"] = "%"
	items[value[0].strip()+".packet_loss"]["name"] = "[{0}] ICMP ping: packet loss".format(value[0].strip())
	items[value[0].strip()+".packet_loss"]["type"] = "float"
	items[value[0].strip()+".packet_loss"]["timestamp"] = int(value[2])

output_json_final = json.dumps(output_json, ensure_ascii=False, indent = 4)
print(output_json_final)