import sys
import os

import urllib.parse
import select
import socket
import queue
import threading

master_root = os.getcwd()
master_root += "/"
master_root += sys.argv[1]

buff_size = 4096

def normalize_url(url):
	if url == "/":
		url += "index.html"
	return urllib.parse.unquote(url)

class ClientHandler(threading.Thread):

	def __init__(self, socket, addr):
		threading.Thread.__init__(self)
		self.socket = socket
		self.addr = addr



	def run(self):
		try:
			data = self.socket.recv(buff_size).decode("utf-8")
			# print(data.decode("utf-8"))
			# while data:
			# 	all_data += data
			# 	data = self.socket.recv(buff_size)
			# 	print("Is this empty: " + data.decode("utf-8"))

			# data = all_data
		except Exception as e:
			print(e)
			print("Тоя пич не иска да ми дава данни, или са зле форматирани данните - не заслужава 500 - ама бъгва ab-то, тъй че заслужава!")
			server_error_file = open(master_root+"/500.html", "rb")

			self.socket.sendfile(server_error_file)

			self.kill_thread()
			return

		try:
			lines = data.split("\n")
			basic_stuff = lines[0]
			method_type, url, http_version = basic_stuff.split(" ")
		except Exception as e:
			print("Тоя пич не ми дава адекватни данни по стандарт")
			server_error_file = open(master_root+"/500.html", "rb")
			self.socket.sendfile(server_error_file)

			self.kill_thread()
			return

		url = urllib.parse.unquote(url)
		self.url = url
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
			try:
				get_arguments = url.split("?")[1].split("&")
			except Exception as e:
				print(e)

			for argument in get_arguments:
				try:
					argument_name, argument_value = argument.split("=")
					get_parameters[argument_name] = argument_value
				except Exception as e:
					# if the get is malformed, dont pass it to the webpage!
					pass

		try:
			with open(file_path, "rb") as f:
				self.socket.sendfile(f)

		except FileNotFoundError as e:
			page_404 = master_root+"/404.html"
			with open(page_404, "rb") as f:
				self.socket.sendfile(f)

		self.socket.close()

	#Accepts some stuff like data and file handler and file pathing,
	#Returns file handler - rb
	def parse_file(self, file_hanler, tmp_file_path, data):
		temp_file = open(tmp_file_path, "w")

		python_code = """"""
		found_python_code = 0
		parse_python_code = 0
		for line in file_hanler:
			if "{{" in line:
				found_python_code = 1
				continue
			if "}}" in line:
				parse_python_code = 1

			if parse_python_code:

				f = io.StringIO()
				errors_in_python_code = 0
				with redirect_stdout(f):
					current_url = self.url
					try:
						exec(python_code, locals(), locals())
					except Exception as e:
						print(e)
						errors_in_python_code = 1

				if errors_in_python_code:
					temp_file.close()
					try:
						print("Лошичък код!")
						server_error_file = open(master_root+"/500.html", "rb")
					except FileNotFoundError as e:
						print(e)
						# we hope we never get here!
						no_file = open(master_root+"/404.html", "rb")
						return no_file
					return server_error_file


				for python_code_output_line in f.getvalue().split("\n"):
					temp_file.write(python_code_output_line)
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

	def kill_thread(self):
		try:
			self.socket.close()
		except Exception as e:
			print(e)


PORT = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setblocking(0)

try:

	s.bind(('127.0.0.1', PORT))

except OSError as e:
	print(e)
	sys.exit(1)
	
s.listen(5)
print("Socket is waiting for connection on 127.0.0.1:80/")

inputs = [s]
outputs = []
exceptions = []

message_queues = {}

while inputs:
	readable, writable, exceptional = select.select(inputs, outputs, exceptions, 120)

	for socket in readable:
		if socket is s:
			connection, client_address = s.accept()
			connection.setblocking(0)
			inputs.append(connection)

		else:
			data = socket.recv(buff_size)
			message_queues[socket] = data
			if data:
				#print('  received {!r} from {}'.format(data, socket.getpeername()))
				outputs.append(socket)
				inputs.remove(socket)
			else:
				inputs.remove(socket)
				del message_queues[socket]
				socket.close()

	for socket in writable:
		if not socket in message_queues:
			with open(master_root+"/500.html", "rb") as f:
				data = f.read(4096)
				while data:
					socket.send(data)
					data = f.read(4096)
		else:
			url = message_queues[socket].decode("utf-8").split("\n")[0].split(" ")[1]
			url = normalize_url(url)
			try:
				with open(master_root + url, "rb") as f:
					data = f.read(4096)
					while data:
						socket.send(data)
						data = f.read(4096)	
			except FileNotFoundError as e:
				with open(master_root + "/404.html", "rb") as f:
					data = f.read(4096)
					while data:
						socket.send(data)
						data = f.read(4096)

		outputs.remove(socket)
		del message_queues[socket]
		socket.close()


	for socket in exceptional:
		if socket in inputs:
			inputs.remove(socket)
		if socket in exceptions:
			exceptions.remove(socket)
		if socket in outputs:
			outputs.remove(socket)
		
		del message_queues[socket]
		socket.close()
