import socket
from urllib import parse

filename = "/home/todor/Desktop/python_scripts/big.txt"

buff_size = 1024 * 64

request = b"""POST /?filename={0} HTTP/1.1\r\nHost: 127.0.0.1\r\nUser-Agent:Mozilla/5.0 (X11;Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nContent-Type: image/jpeg\r\nContent-Length: {1}\r\nConnection:keep-alive\r\n\r\n"""

sockets = []
HOST = "127.0.0.1"
PORT = 80

for k in range(10):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	sockets.append(s)

with open(filename, "rb") as f:
	f.seek(0, 2)
	size = f.tell()
	print(size)
	my_request = bytes(str(request, "utf-8").format("good.txt", size), "utf-8")

	f.seek(0, 0)

	for socket in sockets:
		socket.send(my_request)

	data = f.read(buff_size)
	while data:
		for socket in sockets:
			socket.send(data)
