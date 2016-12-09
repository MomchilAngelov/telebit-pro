import socket
import time

my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


my_sock.connect(('127.0.0.1', 80))

data_array = [b'G', b'E', b'T', b' ', b'/', b' ', b'H', b'T', b'T', b'P', b'/', b'1', b'.', b'1', b'\r', b'\n']

for byte in data_array:
	my_sock.send(byte)
	time.sleep(2)