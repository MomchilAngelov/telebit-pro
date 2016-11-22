import socket
import sys
import os
import threading

master_root = os.getcwd()
master_root += "/"
master_root += sys.argv[1]

buff_size = 4096

class ClientHandler(threading.Thread):

	def __init__(self, user_id, socket, addr):
		threading.Thread.__init__(self)
		self.user_id = user_id
		self.socket = socket
		self.addr = addr

	def run(self):
		data_to_send = ""
		data = self.socket.recv(buff_size)
		print(data.decode("utf-8"))

		if data:
			print("нещо си")
			data = self.socket.recv(buff_size)
			print(data.decode("utf-8"))

		print("хере")

		data = data.decode("utf-8")
		lines = data.split("\n")

		basic_stuff = lines[0]

		method_type, url, http_version = basic_stuff.split(" ")

		if url.split("/")[-1] == "":
			url += "index.html"

		if "?" in url:
			has_get_params = True
		else:
			has_get_params = False

		file_path = master_root
		if has_get_params:
			file_path += url.split("?")[0]
		else:
			file_path += url

		# GET parameters handled! (put in another function)
		get_parameters = {}
		if has_get_params:

			get_arguments = url.split("?")[1].split("&")
			for argument in get_arguments:
				argument_name, argument_value = argument.split("=")
				get_parameters[argument_name] = argument_value

		try:

			with open(file_path, "rb") as f:
				self.socket.sendfile(f)

		except FileNotFoundError as e:
			with open(master_root+"404.html", "rb") as f:
				self.socket.sendfile(f)			
		self.socket.close()

HOST = '127.0.0.1'
PORT = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:

	s.bind((HOST, PORT))

except OSError as e:
	print(e)
	sys.exit(1)
	
s.listen(100)

i = 1
while 1:
	try:
		print("Awaiting connection...")
		connection_socket, addr = s.accept()
		print("Connection got!")
		print("User number {0}".format(i))
		clientHandler = ClientHandler(user_id = i, socket = connection_socket, addr = addr)
		clientHandler.run()
		i += 1

	except KeyboardInterrupt as e:
		print("Shutting down the server!")
		s.close()