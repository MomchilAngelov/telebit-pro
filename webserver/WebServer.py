import sys
import os
import urllib.parse
from urllib.parse import urlparse, parse_qs
import select
import socket
import queue
import threading

master_root = os.getcwd()
master_root += "/"
master_root += sys.argv[1]

CLOSE_CONNECTION = 0
KILL_CONNECTION = 2
file_id = 0

class MySocketWrapper():

	def __init__(self, socket):
		self.socket = socket
		self.buff_size = 1024*1024
		self.url = ""
		self.data = bytes()
		self.fileHandler = None
		self.to_read = 0
		self.qs = {}
		self.headers = {}
		self.chunks = []
		self.my_uploaded_file = None
		self.to_where = 0
		self.filename = ""
		self.flag_for_uploaded_file = 0

	def parse_first_line(self, line):
		try:
			first_line_split = line.split(" ")
			self.method = first_line_split[0]
			self.url = first_line_split[1]
			self.normalize_url()
			self.qs = parse_qs(urlparse("http://" + HOST + self.url).query)
			self.protocol = first_line_split[2]
		except Exception as e:
			print(e)
			return KILL_CONNECTION

	def get_headers(self, headers):
		for line in headers:
			try:
				header_name, header_value = line.split(":", 1)
				header_name = header_name.strip()
				header_value = header_value.strip()
				self.headers[header_name] = header_value
			except Exception as e:
				print(e)
				continue
	
		if "Content-Length" in self.headers:
			try:
				self.to_read += int(self.headers["Content-Length"])
			except Exception as e:
				print(e)

	def started_uploading(self):
		return self.filename is not ""

	def read(self):
		data_received = self.socket.recv(self.buff_size)

		if self.url is "":
			headers_bytes = data_received.split(b"\r\n\r\n")[0]
			self.to_read += len(headers_bytes)
		
			headers = headers_bytes.decode("utf-8")
			header_lines = headers.split("\n")
			
			result = self.parse_first_line(header_lines[0])
			if result == KILL_CONNECTION:
				return KILL_CONNECTION


			self.get_headers(header_lines[1:])

		self.data += data_received
		self.to_read -= self.buff_size
		if self.to_read < 0:
			return CLOSE_CONNECTION
		else:
			return 1			


	def write(self):
		if self.method == "GET":
			if self.fileHandler is None:
				try:
					self.fileHandler = open(master_root + self.url, "rb")
				except FileNotFoundError as e:
					self.fileHandler = open(master_root + "/404.html", "rb")
				except Exception as e:
					self.fileHandler = open(master_root + "/500.html", "rb")
					print(e)

			try:
				data_to_send = self.fileHandler.read(self.buff_size)
			except Exception as e:
				print(e)
				self.close()			
				return CLOSE_CONNECTION
				
			if not data_to_send:
				self.close()
				return CLOSE_CONNECTION
			else:
				try:
					self.socket.send(data_to_send)
				except Exception as e:
					print(e)
					self.close()
					return CLOSE_CONNECTION
			
			return 1

		elif self.method == "POST":
			if not self.started_uploading():

				if "filename" in self.qs:
					self.filename = self.qs["filename"]
					try:

						self.filename_without_extension, self.file_extension = self.filename[0].rsplit(".", 2)

					except Exception as e:
						print("Счупване при парсването на името на файла\n" + str(e))
						self.close()
						return CLOSE_CONNECTION

					if "/" in self.filename_without_extension:
						self.filename_without_extension = self.filename_without_extension.replace("/", "|")

					if "/" in self.file_extension:
						self.file_extension = self.file_extension.replace("/", "|")

					try:
						bytes_body_of_request = self.data.split(b"\r\n\r\n", 2)[1]
					
					except Exception as e:
						print(e)
						print("Малформирана заявка")
						self.close()
						return CLOSE_CONNECTION

					print(len(self.data))
					print(self.headers["Content-Length"])
					self.chunks = [self.data[i:i+self.buff_size] for i in range(0, int(self.headers["Content-Length"]), self.buff_size)]
				else:
					self.close()
					return CLOSE_CONNECTION	
			
			else:
				global file_id
				if self.my_uploaded_file is None:
					
					try:

						self.my_uploaded_file = open(master_root + "/uploads/" + self.filename_without_extension + str(file_id) + "." + self.file_extension, "wb")
					
					except Exception as e:
						print(e)
						self.close()
						return CLOSE_CONNECTION

				file_id += 1

				if not len(self.chunks) == self.to_where:
					
					try:
						self.my_uploaded_file.write(self.chunks[self.to_where])

					except Exception as e:
						print(e)
						os.remove(self.my_uploaded_file)
						self.close()
						return CLOSE_CONNECTION

					self.to_where += 1
				else:
					
					if self.flag_for_uploaded_file == 0:
						self.flag_for_uploaded_file = 1

						try:
							self.my_uploaded_file.close()
						except Exception as e:
							print(e)
							self.close()
							return CLOSE_CONNECTION

					if self.fileHandler is None:
						try:
							self.fileHandler = open(master_root + "/successfull.html", "rb")
						except FileNotFoundError as e:
							self.fileHandler = open(master_root + "/404.html", "rb")
						except Exception as e:
							self.fileHandler = open(master_root + "/500.html", "rb")
							print(e)

					try:
						data_to_send = self.fileHandler.read(self.buff_size)
					except Exception as e:
						print(e)
						self.close()			
						return CLOSE_CONNECTION
						
					if not data_to_send:
						self.close()
						return CLOSE_CONNECTION
					else:
						try:
							self.socket.send(data_to_send)
						except Exception as e:
							print(e)
							self.close()
							return CLOSE_CONNECTION
					
				return 1
			
		else:
			print("We dont support this!")
			self.close()
			return CLOSE_CONNECTION


	def fileno(self):
		return self.socket.fileno()

	def normalize_url(self):
		if self.url == "/":
			self.url += "index.html"
		return urllib.parse.unquote(self.url)

	def close(self):
		try:
			self.fileHandler.close()
		except Exception as e:
			#already closed probably - still checking with print tho
			pass

		try:
			self.my_uploaded_file.close()
		except Exception as e:
			#already closed probably - still checking with print tho
			pass
		
		try:
			self.socket.close()
		except Exception as e:
			#already closed probably - still checking with print tho
			pass


PORT = 80
HOST = '127.0.0.1'
try:
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.setblocking(0)
	server_socket.bind((HOST, PORT))
except Exception as e:
	print(e)
	sys.exit(1)
	

try:
	server_socket.listen(5)
except Exception as e:
	print(e)
	sys.exit(1)

server_socket_wrapped = MySocketWrapper(server_socket)

print("Socket is waiting for connection on 127.0.0.1:80/")

inputs = [server_socket_wrapped]
outputs = []
exceptions = []

try:
	while inputs:
		try:
			readable, writable, exceptional = select.select(inputs, outputs, [], 120)
		except Exception as e:
			print(e)
			continue

		for socket_wrapped in readable:
			if socket_wrapped is server_socket_wrapped:
				try:
					connection, client_address = server_socket_wrapped.socket.accept()
					print("Got connection from {0}".format(connection))
				except Exception as e:
					print(e)
					continue

				try:
					connection.setblocking(0)
				except Exception as e:
					print(e)					
					try:
						connection.close()
					except Exception as e:
						print(e)
						continue
					continue

				new_socket_wrapped = MySocketWrapper(connection)
				inputs.append(new_socket_wrapped)

			else:
				result = socket_wrapped.read()
				if result == CLOSE_CONNECTION:
					inputs.remove(socket_wrapped)
					outputs.append(socket_wrapped)

				if result == KILL_CONNECTION:
					inputs.remove(socket_wrapped)


		for socket_wrapped in writable:
			result = socket_wrapped.write()

			if result == CLOSE_CONNECTION:
				outputs.remove(socket_wrapped)

except KeyboardInterrupt as e:
	print("Shutting server down...")
	server_socket_wrapped.close()
	print("Server is shut down...")