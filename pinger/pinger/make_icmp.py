import socket, struct, time

def makeGoodPacket(input_data_better_be_quallifier):
	ICMP_ECHO_REQUEST = 8
	fullPacketSize = 64
	sizeOfSentPacket = fullPacketSize
	sizeOfSentPacket -= 8
	checkSum = 0
	my_bytes = struct.calcsize("d")
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, checkSum, input_data_better_be_quallifier, 1)

	data = (fullPacketSize - my_bytes) * "Q"
	data = struct.pack("d", time.time()) + bytes(data, "utf-8")

	checkSum = checksum(header + data)

	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(checkSum), input_data_better_be_quallifier, 1)
	packet = header + data

	return packet

def readPacket(packet):
	icmpHeader = packet[20:28]
	type, code, checksum, data, sequence = struct.unpack("bbHHh", icmpHeader)
	return data


def checksum(source_string):
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


for idx, ip in enumerate(ips):
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
	packet = makeGoodPacket(2 * idx)
	my_socket.sendto(packet, (ips[0], 1))
	received_packet, addr = my_socket.recvfrom(64) 
	data = readPacket(received_packet)
	print(data)
	


