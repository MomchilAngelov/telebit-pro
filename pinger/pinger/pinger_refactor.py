import gevent
from gevent import Timeout
from gevent.subprocess import Popen, PIPE, STDOUT
from dicttoxml import dicttoxml

import re, time, json, argparse, sys, socket, glob, tempfile, xml.dom.minidom
from shutil import which

if not 	which("ping"):
	print("We need 'ping' to work...")
	sys.exit(1)

parser = argparse.ArgumentParser(description = """Ping some ips and hosts ;)""")
parser.add_argument("-o", "--output", help="Output format", type = str, choices=["json", "xml"], default="json")
parser.add_argument("-c", "--configure", help="Give the ip json file", type = str, default = False)
parser.add_argument("-p", "--packet", help="The number of packets sent to the host/ip", type = int, default = False)
parser.add_argument("-t", "--time", help="The time the packets should be bashed on the host!", type = int, default = False)
parser.add_argument("-v", "--verbose", help="Give the script more verbosity, make it yell!", action = "store_true", default = False)
args = parser.parse_args()

DEBUG = args.verbose 

versionNumber = "3.0"
applicationName = "Momo's Pinger"
defaultSearchFolder = "test_Data/input.json"

class Resolver():

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

	def resolveDomainName(self, hostname):
		
		hostname = self.normalizeInputForHostname(hostname)

		try:
			ips = socket.gethostbyname_ex(hostname)[2]
		except socket.gaierror as e:
			if DEBUG:
				print("Had problem resolving", hostname)
			ips=[hostname]

		if DEBUG:
			print(hostname, "resolved to", ips)
		
		return ips


class DataGiver():

	def __init__(self):
		pass

	def getDataFromFile(self, file, resolver):
		if DEBUG:
			print("Getting data from {0}".format(file))

		tmp_arr = []

		files_matching_pattern = glob.glob(file)
		if len(files_matching_pattern) > 1:
			input_json = self.openJSON(self.concatenateFiles(files_matching_pattern))
		else:
			try:
				input_json = self.openJSON(files_matching_pattern[0])
			except Exception as e:
				print("No file found...")
				sys.exit()

		for application_name in input_json["applications"]:
			if DEBUG:
				print("Parsing for application...", application_name)
		
			for idx, valueIdx in input_json["applications"][application_name]["items"].items():
				temporary_item = []
				if resolver.isGoodIPv4(valueIdx["address"]):
					temporary_item.append(valueIdx["address"])
					temporary_item.append(valueIdx["packets_count"])
					temporary_item.append(valueIdx["packet_interval"])
					temporary_item.append(None)
					temporary_item.append(application_name)
					temporary_item.append(input_json["applications"][application_name]["name"])
					tmp_arr.append(temporary_item)
				else:
					domain_to_ips = resolver.resolveDomainName(valueIdx["address"])
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

	def concatenateFiles(self, array_of_files):

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

	def openJSON(self, file):
		try:
			with open(file, "r") as f:
				result_json = json.load(f)
		except TypeError:
			file.seek(0)
			return_json = json.load(file)
			file.close()
			return return_json
		return result_json


class DataProccessor():

	def parseResult(self, some_string):

		if "rtt min/avg/max/mdev" in some_string:
			packet_loss_group = re.search(r"(?<=received, )[0-9]+", some_string)
			packet_loss = packet_loss_group.group(0)
			rtt_group = re.search(r"(?<=mdev = )\d+\.\d+/\d+\.\d+/\d+\.\d+/\d+\.\d+", some_string)
			values_arr = rtt_group.group(0).split("/")
			rtt_avg = float(values_arr[1])
			mdev = float(values_arr[3])
			return packet_loss, rtt_avg, mdev
		
		elif "Destination Net Unreachable" in some_string:
			packet_loss_group = re.search(r"([0-9]+)(?=% packet loss)", some_string)
			packet_loss = packet_loss_group.group(0)

			return packet_loss, "N/A", "N/A"

		elif "Network is unreachable" in some_string:
			return 100, "N/A", "N/A"

		elif "unknown host" in some_string:
			return "N/A", "N/A", "N/A"

		else:
			packet_loss_group = re.search(r"([0-9]+)(?=% packet loss)", some_string)
			packet_loss = packet_loss_group.group(0)

			return packet_loss, "N/A", "N/A"


class Outputter():

	def __init__(self, versionNumber, applicationName):
		self.outputDictionary = {}
		self.outputDictionary["version"] = versionNumber
		self.outputDictionary["name"] = applicationName
		self.outputDictionary["applications"] = {}

	def createRootForApplications(self, data):
		previous_value = None
		for key, list_with_command_result in data.items():
			if not list_with_command_result[5] == previous_value:
				previous_value = list_with_command_result[5]
				self.outputDictionary["applications"][list_with_command_result[5]] = {}
				self.outputDictionary["applications"][list_with_command_result[5]]["name"] = list_with_command_result[6]
				self.outputDictionary["applications"][list_with_command_result[5]]["items"] = {}

	def appendItemToOutputter(self, rtt_avg, packet_loss, list_with_command_result):
		items = self.outputDictionary["applications"][list_with_command_result[5]]["items"]
		
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

	def getResultInJSON(self):
		return json.dumps(self.outputDictionary, ensure_ascii=False, indent = 4)

	def getResultInXML(self):
		return xml.dom.minidom.parseString(str(dicttoxml(self.outputDictionary, custom_root='root', attr_type=False), "utf-8")).toprettyxml()

	def getResult(self, outputFormat):
		return eval("self.getResultIn"+(outputFormat.upper())+"()")




def getInitialValues(time, packet):
	if time == 0 and packet == 0:
		return 2, 10

	if time == 0 and packet != 0:
		return packet*0.2, packet

	if time != 0 and packet == 0:
		return time, time*5

	return time, packet

def ping(ip, number_of_packages, current_order, speed, host, data, requesting_application, requesting_application_name):
	command = 'ping -i {0} -W {1} -c {2} {3}'.format(speed, speed * number_of_packages, number_of_packages, ip)
	if DEBUG:
		print(command)

	sub = Popen([command], stdout=PIPE, stderr=STDOUT, shell=True)
	out, err = sub.communicate()
	data[current_order] = [ip, out, time.time(), host, command, requesting_application, requesting_application_name]

def main():
	all_threads = []
	data = {}
	host_to_ip = {}
	outputDictionary = {}

	resolver = Resolver()
	data_giver = DataGiver()
	data_proccessor = DataProccessor()
	outputter = Outputter(versionNumber = versionNumber, applicationName = applicationName)

	if not (args.time == 0 or args.packet == 0):
		if args.time/args.packet < 0.2:
			print("We can't do that...\nYou are going too fast!")
			sys.exit()

	timeout_seconds, package_count = getInitialValues(args.time, args.packet)
	host_to_data = data_giver.getDataFromFile(args.configure or defaultSearchFolder, resolver = resolver)

	all_threads = [gevent.spawn(ping, ip = current_data[0], number_of_packages = current_data[1], 
		current_order = current_order, speed = current_data[2], 
		host = current_data[3], data = data, requesting_application = current_data[4], requesting_application_name = current_data[5])
		for current_order, current_data in enumerate(host_to_data)	
	]

	gevent.joinall(all_threads)

	outputter.createRootForApplications(data)

	for key, list_with_command_result in data.items():
		packet_loss, rtt_avg, mdev = data_proccessor.parseResult(list_with_command_result[1].decode())
		outputter.appendItemToOutputter(rtt_avg, packet_loss, list_with_command_result)

	print(outputter.getResult(outputFormat=args.output))

main()
