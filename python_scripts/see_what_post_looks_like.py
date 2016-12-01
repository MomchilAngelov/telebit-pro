import socket

ip = socket.gethostbyname('www.example.com')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, 80))
s.send(b"GET / HTTP/1.1\r\n\r\n")

data = s.recv(1024)
while data:
	print(data, end="")
	data = s.recv(1024)
