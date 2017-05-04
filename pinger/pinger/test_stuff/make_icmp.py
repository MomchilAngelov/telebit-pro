import socket, struct, time, gevent
from gevent import socket

class Pinger():

	def __init__(self, data, _id, _number_of_pings, _timeout, ip):
		self.data = data
		self._id = _id
		self._number_of_pings = _number_of_pings
		self._timeout = _timeout
		self.curr_ping = 0
		self.ip = ip
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
		self.socket.settimeout(self._timeout)
		self.socket.connect((self.ip, 0))
		self.total_time = 0

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

	def ping(self):
		self.data[self._id] = []
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
				self.data[self._id].append(1)
				self.total_time += self.end_time - self.start_time

		self.data[self._id].append(self._number_of_pings)
		self.data[self._id].append(self.total_time/self._number_of_pings)
		self.socket.close()

ips = [
	"54.192.44.145",
	'40.117.226.146',
	'104.40.225.204',
	'108.168.254.175',
	'108.168.254.173',
	'176.32.100.59',
	'52.35.191.198',
	'54.186.162.9',
	'194.226.130.226',
	'194.226.130.227',
	'194.226.130.228',
	'194.226.130.229'
]

pings = []
data = {}

for idx, ip in enumerate(ips):
	pinger = Pinger(data = data, _id = idx, _number_of_pings = 3, _timeout = 1, ip = ip)
	pings.append(gevent.spawn(pinger.ping))

gevent.joinall(pings)

for key, data  in data.items():
	avg_rtt = data.pop()
	top = data.pop()
	print("Average time: {0:.2f}ms".format((avg_rtt) * 1000))
	print("{0} => {1}/{2}, Packet Loss: {3}%".format(key, sum(data), top, (1-(sum(data)/top)) * 100))
