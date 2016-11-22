import socket
import sys
import os
import random
import threading
import subprocess
from contextlib import redirect_stdout
import io

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
		lines = self.socket.recv(buff_size).decode("utf-8").split("\n")
		
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

		get_parameters = {}
		if has_get_params:

			get_arguments = url.split("?")[1].split("&")
			for argument in get_arguments:
				argument_name, argument_value = argument.split("=")
				get_parameters[argument_name] = argument_value

		try:

			with open(file_path, "r") as f:
				tmp_file_path = master_root + "/tmp/{0}.html".format(random.uniform(1, 10))
				
				tmp_file = self.parse_file(f, tmp_file_path, get_parameters)

				self.socket.sendfile(tmp_file)
				tmp_file.close()
				os.remove(tmp_file_path)

		except FileNotFoundError as e:
			print(e)
			with open(master_root+"/404.html", "rb") as f:
				self.socket.sendfile(f)			
		self.socket.close()

	def parse_file(self, file_hanler, tmp_file_path, data):
		temp_file = open(tmp_file_path, "w")

		python_code = """"""
		found_python_code = 0
		parse_python_code = 0
		for line_number, line in enumerate(file_hanler, 1):
			if "{{" in line:
				found_python_code = 1
				continue
			if "}}" in line:
				parse_python_code = 1

			if parse_python_code:

				f = io.StringIO()
				with redirect_stdout(f):
					exec(python_code, {}, locals())

				for python_code_output_line in f.getvalue().split("\n"):
					temp_file.write(python_code_output_line + "<br />")
				parse_python_code = 0
				found_python_code = 0
				python_code = ""
				continue

			if found_python_code:
				python_code += line
				continue

			temp_file.write(line)

		temp_file.close()
		temp_file = open(tmp_file_path, "rb")

		return temp_file


HOST = '127.0.0.1'
PORT = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:

	s.bind((HOST, PORT))

except OSError as e:
	print(e)
	sys.exit(1)
	
s.listen(10)

i = 1
while 1:
	try:
		print("Awaiting connection...")
		connection_socket, addr = s.accept()
		print("Connection got!")
		print("User number {0}".format(i))
		clientHandler = ClientHandler(user_id = i, socket = connection_socket, addr = addr)
		clientHandler.run()
		print("Connection lost!")
		i += 1

	except KeyboardInterrupt as e:
		print("Shutting down the server!")
		s.close()