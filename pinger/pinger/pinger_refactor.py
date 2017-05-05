#!/usr/bin/env python3

import time, json, argparse, sys, struct, gevent, socket
from dicttoxml import dicttoxml

from error_handling_library import test_hooks
from libs.outputDataIntoDict import Outputter
from libs.dataGiver import DataGiver
from libs.Resolver import Resolver

parser = argparse.ArgumentParser(description = """Ping some ips and hosts ;)""")
parser.add_argument("-o", "--output", help="Output format", type = str, choices=["json", "xml"], default="json")
parser.add_argument("-c", "--configure", help="Give the ip json file", type = str, default = False)
parser.add_argument("-d", "--directory", help="Put the output in written directory. WIll be created if not there.", type = str, default = False)

args = parser.parse_args()

versionNumber = "3.0"
applicationName = "Momo's Pinger"

defaultSearchFolder = "test_Data/input.json"
defaultOutputFolder = "output_data"

searchFolder = args.configure or defaultSearchFolder
outputFolder = args.directory or defaultOutputFolder

ICMP_CONSTANT = socket.getprotobyname('icmp')

OPENED_SOCKETS = 0
CURRENT_TRY_TO_BE_OPENED_SOCKETS = 0

SHOULD_ACCEPT_MORE_SOCKETS = 1

MAX_OPENED_SOCKETS = 500
PROCESS_START_TIME = time.time()


ALL_PINGERS = []

def should_block_sockets():
	global SHOULD_ACCEPT_MORE_SOCKETS
	global CURRENT_TRY_TO_BE_OPENED_SOCKETS

	if OPENED_SOCKETS > MAX_OPENED_SOCKETS:
			SHOULD_ACCEPT_MORE_SOCKETS = 0
	else:
		SHOULD_ACCEPT_MORE_SOCKETS = 1

	while not SHOULD_ACCEPT_MORE_SOCKETS:
		gevent.sleep(2)
		if OPENED_SOCKETS > MAX_OPENED_SOCKETS:
			SHOULD_ACCEPT_MORE_SOCKETS = 0
		else:
			SHOULD_ACCEPT_MORE_SOCKETS = 1

	CURRENT_TRY_TO_BE_OPENED_SOCKETS -= 1


class Statistics():

	def printData(self):

		import resource
		
		last_time = 0
		last_sum_of_cpu_usage = 0

		while 1:
			print("Opened sockets: {0}|Sockets That want to be opened: {1}| Current unresolved hosts: {2}| Currently Resolved Hosts: {5}|Host number: {3}|Greenlets that try to resolve their domain: {4}"
				.format(OPENED_SOCKETS, CURRENT_TRY_TO_BE_OPENED_SOCKETS, OPENED_HOSTS, CURRENT_HOST, CURRENT_IN_GETHOSTBYNAME_EX, CURRENT_HOST - OPENED_HOSTS))
			
			resource_giver = resource.getrusage(resource.RUSAGE_SELF)
			
			print("Max ram Usage: {0}MB".format(resource_giver.ru_maxrss/1024), end=" ")
			sum_of_cpu_usage = resource_giver.ru_utime + resource_giver.ru_stime
			time_now = time.time()
			time_since_start = time_now - PROCESS_START_TIME

			print("Average CPU time: {0}%".format((sum_of_cpu_usage / time_since_start) * 100), end=" ")
			print("Current CPU time: {0}%".format((sum_of_cpu_usage - last_sum_of_cpu_usage) / (time_now - last_time) * 100))

			last_time = time.time()
			last_sum_of_cpu_usage = sum_of_cpu_usage

			gevent.sleep(1)


class Pinger():

	def __init__(self, item):
		global OPENED_SOCKETS
		self.data = item
		self._id = int(item['idx'])
		self._number_of_pings = item['packets_count']
		self._timeout = item['packet_interval']
		self.curr_ping = 0
		self.ip = item['ip']
		self.address = item['address']
		should_block_sockets()
		OPENED_SOCKETS += 1
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CONSTANT)
		except Exception as e:
		 	print("Please use sudo when using the ICMP pinger...")
		 	sys.exit(1)

		self.socket.settimeout(self._timeout)
		self.total_time = 0
		self.total_received_packets = 0

	def makeGoodPacket(self):
		ICMP_ECHO_REQUEST = 8; fullPacketSize = 64; sizeOfSentPacket = fullPacketSize; sizeOfSentPacket -= 8; checkSum = 0;
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

		try:
			self.socket.connect((self.ip, 0))
		except Exception as e:
			self.data['timestamp'] = time.time()
			self.data['packet_loss'] = "N/A"
			self.data['rtt'] = "N/A"

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
				pass
			
			try:
				received_packet, addr = self.socket.recvfrom(64)
				data = self.readPacket(received_packet)
				self.end_time = time.time()
			except Exception as e:
				pass
			else:
				self.curr_ping += 1 
				self.total_received_packets += 1
				self.total_time += self.end_time - self.start_time

		packet_loss = (1-(self.total_received_packets/self._number_of_pings)) * 100

		self.data['timestamp'] = time.time()
		self.data['packet_loss'] = packet_loss

		if packet_loss == 100:
			self.data['rtt'] = "N/A"
		else:
			self.data['rtt'] = (self.total_time/self._number_of_pings) * 1000

		self.socket.close()
		OPENED_SOCKETS -= 1

		outputter.appendItemToOutputter(self.data)


def main():
	data_giver = DataGiver()
	outputter = Outputter(versionNumber = versionNumber, applicationName = applicationName)
	resolver = Resolver(outputter = outputter, class_of_pinger = Pinger, should_resolve = True)

	data = gevent.spawn(data_giver.getDataFromFile, searchFolder, resolver)
	data.join()

	print(outputter.getResult(outputFormat = args.output))

main()
