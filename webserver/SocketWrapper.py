import sys
import os
import os.path
import urllib.parse
from urllib.parse import urlparse, parse_qs
import select
import socket

CLOSE_CONNECTION = 0
KILL_CONNECTION = 2
file_id = 0

PORT = 80
HOST = '127.0.0.1'

master_root = os.getcwd()
master_root += "/"
master_root += sys.argv[1]


class MySocketWrapper():

	def __init__(self, socket):
		self.socket = socket
		#self.buff_size = 1024*1024
		self.buff_size = 1024 * 32
		self.url = ""
		self.data = bytes()
		self.fileHandler = None
		self.first = 0
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
			#print("45:" + str(e))
			#print("Data for exception: " + str(first_line_split))
			return KILL_CONNECTION

	def get_headers(self, headers):
		for line in headers:
			if line is "":
				continue
			try:
				header_name, header_value = line.split(":", 1)
				header_name = header_name.strip()
				header_value = header_value.strip()
				self.headers[header_name] = header_value
			except Exception as e:
				print(line)
				print("57: " + str(e))
				continue
	
		if "Content-Length" in self.headers:
			try:
				self.to_read += int(self.headers["Content-Length"])
			except Exception as e:
				print(e)

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

		if self.method == "POST":

			try:
				filename = self.qs["filename"][0]
			except Exception as e:
				self.socket.send(bytes("Туй трябва да има filename като GET param", "utf-8"))
				self.close()
				return KILL_CONNECTION

			try:
				data_to_write = data_received.split(b"\r\n\r\n")[1]
			except Exception as e:
				data_to_write = data_received

			if not self.fileHandler:
				file_path = master_root + "/uploads/" + filename

				if os.path.isfile(file_path):
					global file_id
					file_id += 1
					files_splitted = file_path.rsplit(".", 1)
					file_path = files_splitted[0] + "({0})".format(file_id) + "." + files_splitted[1]

				self.fileHandler = open(file_path, "wb")

			try:
				bytes_written = self.fileHandler.write(data_to_write)
				#if bytes_written != len(data_to_write):
					#print("There was an error - wrote less than what i received!")
				#	pass
				#if len(data_received) != self.buff_size:
					#print("Got less than I want:\n\tWanted: {0}\n\tGot: {1}".format(self.buff_size ,len(data_received)))
				#	pass
			except Exception as e:
				print(e)

		self.data += data_received
		self.to_read -= len(data_received)
		if self.to_read < 0:
			return CLOSE_CONNECTION
		elif len(data_received) == 0:
			#the file was not fully sent
			try:
				self.fileHandler.close()
				os.remove(self.fileHandler.name)
			except Exception as e:
				print(e)

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
				self.close()			
				return CLOSE_CONNECTION
				
			if not data_to_send:
				self.close()
				return CLOSE_CONNECTION
			else:
				try:
					self.socket.send(data_to_send)
				except Exception as e:
					self.close()
					return CLOSE_CONNECTION
			
			return 1

		else:
			self.socket.send("We dont support this!".encode("utf-8"))
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
