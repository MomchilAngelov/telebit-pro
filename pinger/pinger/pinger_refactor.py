#!/usr/bin/env python3

import gevent


from gevent import Timeout
from dicttoxml import dicttoxml

import re, time, json, argparse, sys, socket, glob, tempfile, xml.dom.minidom, copy, struct
from gevent import socket

parser = argparse.ArgumentParser(description = """Ping some ips and hosts ;)""")
parser.add_argument("-o", "--output", help="Output format", type = str, choices=["json", "xml"], default="json")
parser.add_argument("-c", "--configure", help="Give the ip json file", type = str, default = False)
parser.add_argument("-v", "--verbose", help="Give the script more verbosity, make it yell!", action = "store_true", default = False)
args = parser.parse_args()

DEBUG = args.verbose 

versionNumber = "3.0"
applicationName = "Momo's Pinger"
defaultSearchFolder = "test_Data/input.json"


class Pinger():

	def __init__(self, data, _id, _number_of_pings, _timeout, ip):
		self.im_broken = 0
		self.data = data
		self._id = _id
		self._number_of_pings = _number_of_pings
		self._timeout = _timeout
		self.curr_ping = 0
		self.ip = ip
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
		except IOError as e:
			self.im_broken = 1
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
		while self.im_broken:
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
				self.socket.settimeout(self._timeout)
				self.im_broken = 0
			except IOError as e:
				gevent.sleep(1)

		self.mine_arr = []
		self.data.append(self.mine_arr)
		try:
			self.socket.connect((self.ip, 0))
		except Exception as e:
			self.mine_arr.append(time.time())
			self.mine_arr.append("N/A")
			self.mine_arr.append("N/A")
			self.socket.close()
			outputter.appendItemToOutputter(self.data)

			return

		for x in range(self._number_of_pings):
			packet = self.makeGoodPacket()
			
			try:
				self.socket.send(packet)
				self.start_time = time.time()
			except Exception as e:
				pass
				#print("Error sending packet from ping on Pinger: \n", e)
			
			try:
				received_packet, addr = self.socket.recvfrom(64)
				data = self.readPacket(received_packet)
				self.end_time = time.time()
			except Exception as e:
				pass
				#print("Error receiving packet from ping on Pinger: \n", e)
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

		outputter.appendItemToOutputter(self.data)


class Resolver():

	def __init__(self, threads, outputter):
		self.iterations = 0
		self.threads = threads
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

		hostname = self.normalizeInputForHostname(hostname)

		try:
			ips = socket.gethostbyname_ex(hostname)[2]
		except Exception as e:
			if DEBUG:
				print("Had problem resolving", hostname)
			ips=[hostname]

		if DEBUG:
			print(hostname, "resolved to", ips)
		
		for ip in ips:
			temporary_item = []
			temporary_item.append(ip)
			temporary_item.append(array_with_data["packets_count"])
			temporary_item.append(array_with_data["packet_interval"])
			temporary_item.append(array_with_data["address"])
			temporary_item.append(array_with_data["application_name"])
			temporary_item.append(array_with_data['application_name_human_name'])
			
			appendHere.append(temporary_item)
			self.callDummyPing(temporary_item)
			self.iterations += 1
			if not (self.iterations % 10):
				print(self.iterations)

	def callDummyPing(self, item):
		pinger = Pinger(data = item, _id = len(item), _number_of_pings = item[1], _timeout = item[2], ip = item[0])
		while not pinger:
			pinger = Pinger(data = item, _id = len(item), _number_of_pings = item[1], _timeout = item[2], ip = item[0])

		self.threads.append(gevent.spawn(pinger.ping, self.outputter))

class DataGiver():

	def __init__(self):
		self.domain_to_ips_list = []

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
					valueIdx['application_name'] = application_name
					valueIdx['application_name_human_name'] = input_json["applications"][application_name]["name"]
					valueIdx['idx'] = idx
					self.domain_to_ips_list.append(valueIdx)
					
		if len(self.domain_to_ips_list) > 0:
			array_of_resolvers = [gevent.spawn(resolver.resolveDomainName, should_be_resolved["address"], should_be_resolved, tmp_arr)
				for should_be_resolved in self.domain_to_ips_list	
			]

			gevent.joinall(array_of_resolvers)
		
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

	def createRootForApplications(self, data, name):
		self.outputDictionary["applications"][data] = {}
		self.outputDictionary["applications"][data]["name"] = name
		self.outputDictionary["applications"][data]["items"] = {}

	def appendItemToOutputter(self, output):
		#print(output)
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
	all_threads_2 = []

	data_giver = DataGiver()
	outputter = Outputter(versionNumber = versionNumber, applicationName = applicationName)
	resolver = Resolver(all_threads_2, outputter)

	host_to_data = data_giver.getDataFromFile(args.configure or defaultSearchFolder, resolver = resolver)


	gevent.joinall(all_threads_2)


	#print(outputter.getResult(outputFormat=args.output))

main()
