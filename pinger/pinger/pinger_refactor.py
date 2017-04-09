#!/usr/bin/env python3

import gevent


from dicttoxml import dicttoxml

import re, time, json, argparse, sys, socket, glob, tempfile, xml.dom.minidom, copy, struct, os
from gevent import socket, Timeout 

parser = argparse.ArgumentParser(description = """Ping some ips and hosts ;)""")
parser.add_argument("-o", "--output", help="Output format", type = str, choices=["json", "xml"], default="json")
parser.add_argument("-c", "--configure", help="Give the ip json file", type = str, default = False)
parser.add_argument("-v", "--verbose", help="Give the script more verbosity, make it yell!", action = "store_true", default = False)
parser.add_argument("-s", "--stats", help="Give some statistics on the screen!", action = "store_true", default = False)
parser.add_argument("-d", "--directory", help="Put the output in written directory. WIll be created if not there.", type = str, default = False)

args = parser.parse_args()

DEBUG = args.verbose 
STATS = args.stats

versionNumber = "3.0"
applicationName = "Momo's Pinger"

defaultSearchFolder = "test_Data/input.json"
defaultOutputFolder = "output_data"

searchFolder = args.configure or defaultSearchFolder
outputFolder = args.directory or defaultOutputFolder

#socket.getprotobyname отваря файла на OS-то в /etc/protocols, 
#и мисля че го загнездва там, и ми дава no protocol error като станат повече от 1200 greenlet-а, затова го изнасям
ICMP_CONSTANT = socket.getprotobyname('icmp')

OPENED_SOCKETS = 0
OPENED_HOSTS = 0
CURRENT_HOST = 0
CURRENT_IN_GETHOSTBYNAME_EX = 0

SHOULD_ACCEPT_MORE_HOSTS = 1

MAX_OPENED_SOCKETS = 300 #so far unused
OPENED_HOSTS_MAX = 300
OPENED_HOST_MAX_RETURN = 100

class Statistics():

	def printData(self):
		while 1:
			if STATS:
				print("Opened sockets: {0}| Current unresolved hosts: {1}| Currently Resolved Hosts: {4}|Host number: {2}|Greenlets that try to resolve their domain: {3}"
					.format(OPENED_SOCKETS, OPENED_HOSTS, CURRENT_HOST, CURRENT_IN_GETHOSTBYNAME_EX, OPENED_HOSTS - OPENED_HOSTS))
			gevent.sleep(1)

class Pinger():

	def __init__(self, data, _id, _number_of_pings, _timeout, ip):
		global OPENED_SOCKETS
		self.im_broken = 0
		self.data = data
		self._id = _id
		self._number_of_pings = _number_of_pings
		self._timeout = _timeout
		self.curr_ping = 0
		self.ip = ip
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CONSTANT)
		OPENED_SOCKETS += 1
		self.socket.settimeout(self._timeout)
		self.total_time = 0
		self.total_received_packets = 0

	def makeGoodPacket(self):
		ICMP_ECHO_REQUEST = 8
		fullPacketSize = 64
		sizeOfSentPacket = fullPacketSize
		sizeOfSentPacket -= 8
		checkSum = 0
		my_bytes = struct.calcsize("d")
		header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, checkSum, self._id, 1)

		data = (fullPacketSize - my_bytes) * "Q"
		data = struct.pack("d", time.time()) + bytes(data, "utf-8")

		checkSum = self.checksum(header + data)

		header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(checkSum), self._id, 1)
		packet = header + data

		return packet

	def readPacket(self, packet):
		icmpHeader = packet[20:28]
		type, code, checksum, data, sequence = struct.unpack("bbHHh", icmpHeader)
		return data


	def checksum(self, source_string):
		my_sum = 0
		count_to = (len(source_string) // 2) * 2
		for count in range(0, count_to, 2):
			this = ((source_string[count + 1]) * 256) + source_string[count]
			my_sum += this

		if count_to < len(source_string):
			my_sum = my_sum + ord(source_string[len(source_string) - 1])

		my_sum = (my_sum >> 16) + (my_sum & 0xffff)
		answer = (~(my_sum + (my_sum >> 16))) & 0xffff
		answer = answer >> 8 | (answer << 8 & 0xff00)

		return answer

	def ping(self, outputter):
		global OPENED_SOCKETS
		global SHOULD_ACCEPT_MORE_HOSTS
		global OPENED_HOSTS

		self.mine_arr = []
		self.data.append(self.mine_arr)
		try:
			self.socket.connect((self.ip, 0))
		except Exception as e:
			self.mine_arr.append(time.time())
			self.mine_arr.append("N/A")
			self.mine_arr.append("N/A")
			OPENED_SOCKETS -= 1
			self.socket.close()
			outputter.appendItemToOutputter(self.data)

			return

		for x in range(self._number_of_pings):
			packet = self.makeGoodPacket()
			
			try:
				self.socket.send(packet)
				self.start_time = time.time()
			except Exception as e:
				#print("Error sending packet to {0} on Pinger: \n".format(self.ip), e)
				pass
			
			try:
				received_packet, addr = self.socket.recvfrom(64)
				data = self.readPacket(received_packet)
				self.end_time = time.time()
			except Exception as e:
				#print("Error receiving packet from {0} on Pinger: \n".format(self.ip), e)
				pass
			else:
				self.curr_ping += 1 
				self.total_received_packets += 1
				self.total_time += self.end_time - self.start_time

		packet_loss = (1-(self.total_received_packets/self._number_of_pings)) * 100

		self.mine_arr.append(time.time())
		self.mine_arr.append(packet_loss)
		if packet_loss == 100:
			self.mine_arr.append("N/A")
		else:
			#print("rtt:", self.total_time/self._number_of_pings)
			self.mine_arr.append((self.total_time/self._number_of_pings) * 1000)
	

		self.socket.close()
		OPENED_SOCKETS -= 1
		OPENED_HOSTS -= 1

		outputter.appendItemToOutputter(self.data)

class Resolver():

	def __init__(self, outputter):
		self.iterations = 0
		self.threads = []
		self.outputter = outputter

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

	def resolveDomainName(self, hostname, array_with_data, appendHere):
		global OPENED_HOSTS
		global SHOULD_ACCEPT_MORE_HOSTS
		global CURRENT_HOST
		global CURRENT_IN_GETHOSTBYNAME_EX

		hostname = self.normalizeInputForHostname(hostname)
		
		if OPENED_HOSTS > OPENED_HOSTS_MAX:
			SHOULD_ACCEPT_MORE_HOSTS = 0
		if OPENED_HOSTS < OPENED_HOST_MAX_RETURN:
			SHOULD_ACCEPT_MORE_HOSTS = 1

		while not SHOULD_ACCEPT_MORE_HOSTS:
			gevent.sleep(2)

		try:
			CURRENT_IN_GETHOSTBYNAME_EX += 1
			#We get here almost immediatly, because there is no blocking available
			#This blocks for a bit al the threads, and the code below makes it so not all of them go out, but they still
			#Are here and try to get their host_by_name fixed
			ips = socket.gethostbyname_ex(hostname)[2]
		except Exception as e:
			ips=[hostname]

		CURRENT_IN_GETHOSTBYNAME_EX -= 1
		if OPENED_HOSTS > OPENED_HOSTS_MAX:
			SHOULD_ACCEPT_MORE_HOSTS = 0
		if OPENED_HOSTS < OPENED_HOST_MAX_RETURN:
			SHOULD_ACCEPT_MORE_HOSTS = 1

		while not SHOULD_ACCEPT_MORE_HOSTS:
			gevent.sleep(2)

		for ip in ips:
			temporary_item = []
			temporary_item.append(ip)
			temporary_item.append(array_with_data["packets_count"])
			temporary_item.append(array_with_data["packet_interval"])
			temporary_item.append(array_with_data["address"])
			temporary_item.append(array_with_data["application_name"])
			temporary_item.append(array_with_data['application_name_human_name'])
			
			CURRENT_HOST += 1
			OPENED_HOSTS += 1
			appendHere.append(temporary_item)
			self.callDummyPing(temporary_item)
			self.iterations += 1

		gevent.joinall(self.threads)

	def callDummyPing(self, item):
		pinger = Pinger(data = item, _id = len(item), _number_of_pings = item[1], _timeout = item[2], ip = item[0])
		self.threads.append(gevent.spawn(pinger.ping, self.outputter))


class DataGiver():

	def __init__(self):
		self.threads = []
		self.domain_to_ips_list = []

	def getDataFromFile(self, file, resolver):
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
					valueIdx['application_name'] = application_name
					valueIdx['application_name_human_name'] = input_json["applications"][application_name]["name"]
					valueIdx['idx'] = idx
					self.domain_to_ips_list.append(valueIdx)
					
		if len(self.domain_to_ips_list):
			for should_be_resolved in self.domain_to_ips_list:
				self.threads.append(gevent.spawn(resolver.resolveDomainName, should_be_resolved["address"], should_be_resolved, tmp_arr))

			gevent.joinall(self.threads)

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

	def createRootForApplications(self, data, name):
		self.outputDictionary["applications"][data] = {}
		self.outputDictionary["applications"][data]["name"] = name
		self.outputDictionary["applications"][data]["items"] = {}

	def appendItemToOutputter(self, output):
		rtt = output[6].pop()
		packet_loss = output[6].pop()
		timestamp = output[6].pop()

		try:
			items = self.outputDictionary["applications"][output[4]]["items"]
		except Exception as e:
			self.createRootForApplications(output[4], output[5])
			items = self.outputDictionary["applications"][output[4]]["items"]


		items[output[0].strip()+".rtt"] = {
			"value": rtt, 
			"units": "ms", 
			"name": "[{0} -> {1}] ICMP ping: packet round trip time".format(output[0].strip(), output[3]), 
			"type": "float", 
			"timestamp": int(timestamp), 
			"domain": output[3], 
			"requesting_application": output[5]
		}

		items[output[0].strip()+".packet_loss"] = {
			"value": packet_loss,
			"units": "%", "name": "[{0} -> {1}] ICMP ping: packet loss".format(output[0].strip(), output[3]),
			"type": "float",
			"timestamp": int(timestamp), 
			"domain": output[3],
			"requesting_application": output[5]
		}

	def getResultInJSON(self):
		return json.dumps(self.outputDictionary, ensure_ascii=False, indent = 4)

	def getResultInXML(self):
		return xml.dom.minidom.parseString(str(dicttoxml(self.outputDictionary, custom_root='root', attr_type=False), "utf-8")).toprettyxml()

	def getResult(self, outputFormat):
		return eval("self.getResultIn"+(outputFormat.upper())+"()")


def main():
	if STATS:
		stater = Statistics()
		mark = gevent.spawn(stater.printData)

	data_giver = DataGiver()
	outputter = Outputter(versionNumber = versionNumber, applicationName = applicationName)
	resolver = Resolver(outputter = outputter)

	data = gevent.spawn(data_giver.getDataFromFile, searchFolder, resolver)
	data.join()

	if STATS:
		if not os.path.exists(outputFolder):
			os.makedirs(outputFolder)	
		
		with open("{3}/{0}-{1}-output.{2}".format(time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
			applicationName, args.output, outputFolder), "w") as f:
			f.write(outputter.getResult(outputFormat=args.output))
	else:
		print(outputter.getResult(outputFormat=args.output))

main()
