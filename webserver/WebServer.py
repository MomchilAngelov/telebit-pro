import socket
import sys
import os
import random
import threading
import subprocess
from contextlib import redirect_stdout
import io
import urllib.parse
import datetime

master_root = os.getcwd()
master_root += "/"
master_root += sys.argv[1]

buff_size = 4096


class ClientHandler(threading.Thread):

	def __init__(self, socket, addr):
		threading.Thread.__init__(self)
		self.socket = socket
		self.addr = addr



	def run(self):
		try:
			data = self.socket.recv(buff_size).decode("utf-8")
		except Exception as e:
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

		#print(url)

		try:
			if not url.split("/")[-1].split(".")[1][0:4] == "html":
				dont_parse = True
			else:
				dont_parse = False
		except IndexError as e:
			dont_parse = True

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
			if dont_parse:
				with open(file_path, "rb") as f:
					# if the file isnt .html
					print(file_path)
					self.socket.sendfile(f)

			else:
				with open(file_path, "r") as f:
					tmp_file_path = master_root + "/tmp/{0}.html".format(random.uniform(1, 10))
					
					tmp_file = self.parse_file(f, tmp_file_path, get_parameters)

					self.socket.sendfile(tmp_file)
					tmp_file.close()
					os.remove(tmp_file_path)


		except FileNotFoundError as e:
			page_404 = master_root+"/404.html"
			page_404_tmp = master_root+"/tmp/404.html{0}".format(random.uniform(1, 10))
			with open(page_404, "r") as f:
				tmp_file = self.parse_file(f, page_404_tmp, get_parameters)
				self.socket.sendfile(tmp_file)
				tmp_file.close()
				os.remove(page_404_tmp)

		print("Closing socket!")
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


HOST = '127.0.0.1'
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:

	s.bind((HOST, PORT))

except OSError as e:
	print(e)
	sys.exit(1)
	
s.listen(10)

while 1:
	try:
		connection_socket, addr = s.accept()
		try:
			connection_socket.settimeout(2)
		except Exception as e:
			connection_socket.close()
			continue
		clientHandler = ClientHandler(socket = connection_socket, addr = addr)
		clientHandler.run()

	except KeyboardInterrupt as e:
		print("Shutting down the server!")
		s.close()