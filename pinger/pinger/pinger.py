import gevent
from gevent import Timeout
from gevent.subprocess import Popen, PIPE
import re, time, json, argparse, sys, socket, glob, tempfile

parser = argparse.ArgumentParser(description = """Ping some ips and hosts ;)""")
parser.add_argument("-c", "--configure", help="Give the ip json file", type = str, default = False)
parser.add_argument("-p", "--packet", help="The number of packets sent to the host/ip", type = int, default = False)
parser.add_argument("-t", "--time", help="The time the packets should be bashed on the host!", type = int, default = False)
parser.add_argument("-v", "--verbose", help="Give the script more verbosity, make it yell!", action = "store_true", default = False)
args = parser.parse_args()

DEBUG = args.verbose 

def main():
	all_threads = []
	data = {}
	host_to_ip = {}
	output_json = {}
	versionNumber = "3.0"
	applicationName = "Momo's little Pinger"
	defaultSearchFolder = "test_Data/input.json"

	if not (args.time == 0 or args.packet == 0):
		if args.time/args.packet < 0.2:
			print("We can't do that...\nYou are going too fast!")
			sys.exit()

	timeout_seconds, package_count = getInitialValues(args.time, args.packet)
	host_to_data = getDataFromFile(args.configure or defaultSearchFolder)

	all_threads = [gevent.spawn(ping, ip = current_data[0], number_of_packages = current_data[1], 
		current_order = current_order, speed = current_data[2], 
		host = current_data[3], data = data, requesting_application = current_data[4], requesting_application_name = current_data[5])
		for current_order, current_data in enumerate(host_to_data)	
	]

	gevent.joinall(all_threads)

	output_json["version"] = versionNumber
	output_json["applications"] = {}

	#if old output format should be reversed
	#all in one big items hash, instead of segregated per application that requested it 
	# output_json["applications"]["icmp_pings"] = {}
	# output_json["applications"]["icmp_pings"]["name"] = applicationName
	# output_json["applications"]["icmp_pings"]["items"] = {}
	# items = output_json["applications"]["icmp_pings"]["items"]

	previous_value = None
	for key, list_with_command_result in data.items():
		if not list_with_command_result[5] == previous_value:
			previous_value = list_with_command_result[5]
			output_json["applications"][list_with_command_result[5]] = {}
			output_json["applications"][list_with_command_result[5]]["name"] = list_with_command_result[6]
			output_json["applications"][list_with_command_result[5]]["items"] = {}
			
		
		items = output_json["applications"][list_with_command_result[5]]["items"]

		packet_loss, rtt_avg, mdev = parseResult(list_with_command_result[1].decode())
		
		items[list_with_command_result[0].strip()+".rtt"] = {
			"value": rtt_avg, 
			"units": "ms", 
			"name": "[{0} -> {1}] ICMP ping: packet round trip time".format(list_with_command_result[0].strip(), list_with_command_result[3]), 
			"type": "float", 
			"timestamp": int(list_with_command_result[2]), 
			"domain": list_with_command_result[3], 
			"command": list_with_command_result[4],
			"requesting_application": list_with_command_result[5]
		}

		items[list_with_command_result[0].strip()+".packet_loss"] = {
			"value": packet_loss,
			"units": "%", "name": "[{0} -> {1}] ICMP ping: packet loss".format(list_with_command_result[0].strip(), list_with_command_result[3]),
			"type": "float",
			"timestamp": int(list_with_command_result[2]), 
			"domain": list_with_command_result[3],
			"command": list_with_command_result[4],
			"requesting_application": list_with_command_result[5]
		}
		
		# items[list_with_command_result[0].strip()+".rtt"] = {}	
		# items[list_with_command_result[0].strip()+".rtt"]["value"] = rtt_avg
		# items[list_with_command_result[0].strip()+".rtt"]["units"] = "ms"
		# items[list_with_command_result[0].strip()+".rtt"]["name"] = "[{0} -> {1}] ICMP ping: packet round trip time".format(list_with_command_result[0].strip(), list_with_command_result[3])
		# items[list_with_command_result[0].strip()+".rtt"]["type"] = "float"
		# items[list_with_command_result[0].strip()+".rtt"]["timestamp"] = int(list_with_command_result[2])
		# items[list_with_command_result[0].strip()+".rtt"]["domain"] = list_with_command_result[3]
		# items[list_with_command_result[0].strip()+".rtt"]["command"] = list_with_command_result[4]



		# items[list_with_command_result[0].strip()+".packet_loss"] = {}
		# items[list_with_command_result[0].strip()+".packet_loss"]["value"] = packet_loss
		# items[list_with_command_result[0].strip()+".packet_loss"]["units"] = "%"
		# items[list_with_command_result[0].strip()+".packet_loss"]["name"] = "[{0} -> {1}] ICMP ping: packet loss".format(list_with_command_result[0].strip(), list_with_command_result[3])
		# items[list_with_command_result[0].strip()+".packet_loss"]["type"] = "float"
		# items[list_with_command_result[0].strip()+".packet_loss"]["timestamp"] = int(list_with_command_result[2])
		# items[list_with_command_result[0].strip()+".packet_loss"]["domain"] = list_with_command_result[3]
		# items[list_with_command_result[0].strip()+".packet_loss"]["command"] = list_with_command_result[4]

	output_json_final = json.dumps(output_json, ensure_ascii=False, indent = 4)
	
	print(output_json_final)


def isGoodIPv4(s):

	pieces = s.split('.')
	if len(pieces) != 4: return False	
	try: return all(0<=int(p)<256 for p in pieces)
	except ValueError: return False

def normalizeInputForHostname(hostname):

	hostname = hostname.replace("https://", "", 1)
	hostname = hostname.replace("http://", "", 1)
	if hostname[-1] == "/":
		hostname = hostname[:-1]
	return hostname	

def resolveDomainName(hostname):
	
	hostname = normalizeInputForHostname(hostname)

	try:
		ips = socket.gethostbyname_ex(hostname)[2]
	except socket.gaierror as e:
		if DEBUG:
			print("Had problem resolving", hostname)
		ips=[]

	if DEBUG:
		print(hostname, "resolved to", ips)
	
	return ips

def concatenateFiles(array_of_files):

	temp = tempfile.TemporaryFile(mode="w+")
	my_json = {}
	my_json["version"] = "3.0"
	my_json["applications"] = {}

	for file in array_of_files:
		with open(file) as f:
			tmp_json = json.load(f)
			for k, v in tmp_json["applications"].items():
				my_json["applications"][k] = v

	json.dump(my_json, temp)

	if DEBUG:
		with open("intermidiate_file.json", "w") as f:
			json.dump(my_json, f, indent=4)

	return temp

def openJSON(file):
	try:
		with open(file, "r") as f:
			result_json = json.load(f)
	except TypeError:
		file.seek(0)
		return_json = json.load(file)
		file.close()
		return return_json
	return result_json

def getDataFromFile(file):
	if DEBUG:
		print("Getting data from {0}".format(file))

	tmp_arr = []

	files_matching_pattern = glob.glob(file)
	if len(files_matching_pattern) > 1:
		input_json = openJSON(concatenateFiles(files_matching_pattern))
	else:
		input_json = openJSON(files_matching_pattern[0])
	
	for application_name in input_json["applications"]:
		if DEBUG:
			print("Parsing for application...", application_name)
	
		for idx, valueIdx in input_json["applications"][application_name]["items"].items():
			temporary_item = []
			if isGoodIPv4(valueIdx["address"]):
				temporary_item.append(valueIdx["address"])
				temporary_item.append(valueIdx["packets_count"])
				temporary_item.append(valueIdx["packet_interval"])
				temporary_item.append(None)
				temporary_item.append(application_name)
				temporary_item.append(input_json["applications"][application_name]["name"])
				tmp_arr.append(temporary_item)
			else:
				domain_to_ips = resolveDomainName(valueIdx["address"])
				for ip in domain_to_ips:
					temporary_item.append(ip)
					temporary_item.append(valueIdx["packets_count"])
					temporary_item.append(valueIdx["packet_interval"])
					temporary_item.append(valueIdx["address"])
					temporary_item.append(application_name)
					temporary_item.append(input_json["applications"][application_name]["name"])
					tmp_arr.append(temporary_item)
					temporary_item = []
	
	if DEBUG:
		print(tmp_arr)

	return tmp_arr

def getInitialValues(time, packet):
	if time == 0 and packet == 0:
		return 2, 10

	if time == 0 and packet != 0:
		return packet*0.2, packet

	if time != 0 and packet == 0:
		return time, time*5

	return time, packet

def parseResult(some_string):

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

def ping(ip, number_of_packages, current_order, speed, host, data, requesting_application, requesting_application_name):
	command = 'ping -i {0} -q -W {1} -c {2} {3}'.format(speed, speed * number_of_packages, number_of_packages, ip)
	if DEBUG:
		print(command)

	sub = Popen([command], stdout=PIPE, shell=True)
	out, err = sub.communicate()
	data[current_order] = [ip, out, time.time(), host, command, requesting_application, requesting_application_name]


main()