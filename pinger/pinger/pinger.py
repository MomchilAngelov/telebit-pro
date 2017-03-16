import gevent
from gevent import Timeout
from gevent.subprocess import Popen, PIPE
import re, time, json, argparse, sys, socket

parser = argparse.ArgumentParser(description = """Ping some ips or hosts ;)""")
parser.add_argument("-c", "--configure", help="Give the ip txt file", type = str, default = False)
parser.add_argument("-v", "--verbose", help="Give the script more verbosity, make it yell!", action = "store_true", default = False)
parser.add_argument("-p", "--packet", help="The number of packets sent to the host/ip", type = int, default = False)
parser.add_argument("-t", "--time", help="The time the packets should be bashed on the host!", type = int, default = False)

args = parser.parse_args()

DEBUG = args.verbose 

all_threads = []
data = {}
host_to_ip = {}
output_json = {}
versionNumber = "3.0"
applicationName = "Momo's little Pinger"
defaultSearchFolder = "test_Data/ips"

if not (args.time == 0 or args.packet == 0):
	if args.time/args.packet < 0.2:
		print("We can't do that...\nYou are going too fast!")
		sys.exit()

def isGoodIPv4(s):
	pieces = s.split('.')
	if len(pieces) != 4: return False
	
	try: return all(0<=int(p)<256 for p in pieces)
	except ValueError: return False

def resolveDomainName(hostname):

	try:
		ips = socket.gethostbyname_ex(hostname)[2]
	except socket.gaierror as e:
		ips=[]

	if DEBUG:
		print(hostname, "resolved to", ips)
	
	return ips

def getDataFromFile(file):
	if DEBUG:
		print("Getting data from {0}".format("test_Data/ips"))

	tmp_arr = []

	with open(file, "r") as f:
		for line in f:
			ip_or_host = str(line).strip()
			if isGoodIPv4(ip_or_host):
				tmp_arr.append(ip_or_host)	
			else:
				ips = resolveDomainName(ip_or_host)
				for ip in ips:
					tmp_arr.append([ip_or_host, ip])
				
	return tmp_arr

def getInitialValues(time, packet):
	if time == 0 and packet == 0:
		return 2, 10

	if time == 0 and packet != 0:
		return packet*0.2, packet

	if time != 0 and packet == 0:
		return time, time*5

	return time, packet

def parse_result(some_string):

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

def ping(ip, number_of_packages, current_order, timeout, host):
	#if DEBUG:
	#	print('ping -i {0} -q -W {1} -c {2} {3}'.format(timeout/number_of_packages, timeout, number_of_packages, ip))

	sub = Popen(["ping -i {0} -q -W {1} -c {2} {3}"
		.format(timeout/number_of_packages, timeout, number_of_packages, ip)], stdout=PIPE, shell=True)
	out, err = sub.communicate()
	data[current_order] = [ip, out, time.time(), host]


timeout_seconds, package_count = getInitialValues(args.time, args.packet)

if DEBUG:
	print("Number of sent packets: {0}".format(package_count))
	print("Time to send the packets: {0}".format(timeout_seconds))


host_to_ip = getDataFromFile(args.configure or defaultSearchFolder)

for current_order, current_ip in enumerate(host_to_ip):
	if type(current_ip) == type(''):
		g = gevent.spawn(ping, ip = current_ip, number_of_packages = package_count,
			current_order = current_order, timeout = timeout_seconds, host = None)
	else:
		g = gevent.spawn(ping, ip = current_ip[1], number_of_packages = package_count,
			current_order = current_order, timeout = timeout_seconds, host = current_ip[0])
	
	all_threads.append(g)

gevent.joinall(all_threads)

output_json["version"] = versionNumber
output_json["applications"] = {}
output_json["applications"]["icmp_pings"] = {}
output_json["applications"]["icmp_pings"]["name"] = applicationName
output_json["applications"]["icmp_pings"]["items"] = {}
items = output_json["applications"]["icmp_pings"]["items"]

for key, value in data.items():
	packet_loss, rtt_avg, mdev = parse_result(value[1].decode())
	
	items[value[0].strip()+".rtt"] = {}
	items[value[0].strip()+".rtt"]["value"] = rtt_avg
	items[value[0].strip()+".rtt"]["units"] = "ms"
	items[value[0].strip()+".rtt"]["name"] = "[{0} -> {1}] ICMP ping: packet round trip time".format(value[0].strip(), value[3])
	items[value[0].strip()+".rtt"]["type"] = "float"
	items[value[0].strip()+".rtt"]["timestamp"] = int(value[2])
	items[value[0].strip()+".rtt"]["domain"] = value[3]


	items[value[0].strip()+".packet_loss"] = {}
	items[value[0].strip()+".packet_loss"]["value"] = packet_loss
	items[value[0].strip()+".packet_loss"]["units"] = "%"
	items[value[0].strip()+".packet_loss"]["name"] = "[{0} -> {1}] ICMP ping: packet loss".format(value[0].strip(), value[3])
	items[value[0].strip()+".packet_loss"]["type"] = "float"
	items[value[0].strip()+".packet_loss"]["timestamp"] = int(value[2])
	items[value[0].strip()+".packet_loss"]["domain"] = value[3]

output_json_final = json.dumps(output_json, ensure_ascii=False, indent = 4)
print(output_json_final)