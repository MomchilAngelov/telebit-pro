#!/usr/bin/env python3

import gevent
from gevent import Timeout
from gevent.subprocess import Popen, PIPE, STDOUT
from dicttoxml import dicttoxml

import re, time, json, argparse, sys, socket, glob, tempfile, xml.dom.minidom
from shutil import which

from gping import GPing

if not which("ping"):
	print("We need 'ping' to work...")
	sys.exit(1)

parser = argparse.ArgumentParser(description = """Ping some ips and hosts ;)""")
parser.add_argument("-o", "--output", help="Output format", type = str, choices=["json", "xml"], default="json")
parser.add_argument("-c", "--configure", help="Give the ip json file", type = str, default = False)
parser.add_argument("-v", "--verbose", help="Give the script more verbosity, make it yell!", action = "store_true", default = False)
args = parser.parse_args()

DEBUG = args.verbose 

versionNumber = "3.0"
applicationName = "Momo's Pinger"
defaultSearchFolder = "test_Data/input.json"

class MakePing():

	def __init__(self):
		self.gping = GPing()
		self.times = 0;

	def makeRequest(self, ip, number_of_packages, current_order, speed, host, data, requesting_application, requesting_application_name):
		self.gping.send(hostname, test_callback)

		command = 'ping -i {0} -W {1} -c {2} {3}'.format(speed, speed * number_of_packages, number_of_packages, ip)
		if DEBUG:
			print(command)

		sub = Popen([command], stdout=PIPE, stderr=STDOUT, shell=True)
		out, err = sub.communicate()
		#this should be the output, if we are going to make everything OK
		data[current_order] = [ip, out, time.time(), host, command, requesting_application, requesting_application_name]


	def ping(self, current_datas, data):
		for idx, current_data in enumerate(current_datas):
			self.gping.send(current_data[0], self.magic_callback, idx, current_data, data)
			self.gping.join()

	def magic_callback(self, ping):
		packet_loss = 100-( ping['packages_received']/ping['current_data'][1] ) * 100 
		data_to_write_to = ping['data_to_write_to']
		data_to_write_to[ping['idx']] = [ping['dest_addr'], None, ping['dtime'], ping['current_data'][3], None, ping['current_data'][5]]

		if ping['success']:
			data_to_write_to[ping['idx']].append(ping['delay'])
			data_to_write_to[ping['idx']].append(packet_loss)
		else:
			data_to_write_to[ping['idx']].append("N/A")
			data_to_write_to[ping['idx']].append(packet_loss)


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

		temp = tempfile.TemporaryFile(mode="r+")
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


class Outputter():

	def __init__(self, versionNumber, applicationName):
		self.outputDictionary = {}
		self.outputDictionary["version"] = versionNumber
		self.outputDictionary["name"] = applicationName
		self.outputDictionary["applications"] = {}

	def createRootForApplications(self, data):
		for key, list_with_command_result in data.items():
			if list_with_command_result[5] not in self.outputDictionary["applications"]:
				previous_value = list_with_command_result[5]
				self.outputDictionary["applications"][list_with_command_result[5]] = {}
				self.outputDictionary["applications"][list_with_command_result[5]]["name"] = list_with_command_result[6]
				self.outputDictionary["applications"][list_with_command_result[5]]["items"] = {}

	def appendItemToOutputter(self, list_with_command_result):
		items = self.outputDictionary["applications"][list_with_command_result[5]]["items"]
		
		items[list_with_command_result[0].strip()+".rtt"] = {
			"value": list_with_command_result[6], 
			"units": "ms", 
			"name": "[{0} -> {1}] ICMP ping: packet round trip time".format(list_with_command_result[0].strip(), list_with_command_result[3]), 
			"type": "float", 
			"timestamp": int(list_with_command_result[2]), 
			"domain": list_with_command_result[3], 
			"command": list_with_command_result[4],
			"requesting_application": list_with_command_result[5]
		}

		items[list_with_command_result[0].strip()+".packet_loss"] = {
			"value": list_with_command_result[7],
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


def main():
	all_threads = []
	data = {}
	host_to_ip = {}
	outputDictionary = {}

	resolver = Resolver()
	data_giver = DataGiver()
	outputter = Outputter(versionNumber = versionNumber, applicationName = applicationName)
	request_creater = MakePing()

	host_to_data = data_giver.getDataFromFile(args.configure or defaultSearchFolder, resolver = resolver)

	request_creater.ping(host_to_data, data)

	outputter.createRootForApplications(data)
	for key, list_with_command_result in data.items():
		outputter.appendItemToOutputter(list_with_command_result)

	print(outputter.getResult(outputFormat=args.output))

main()
