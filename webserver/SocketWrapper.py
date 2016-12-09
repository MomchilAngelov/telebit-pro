import sys
import os
import os.path
import urllib.parse
from urllib.parse import urlparse, parse_qs
import select
import socket
import time
import errno

from pathing_string import *
import util

CLOSE_CONNECTION = 0
KILL_CONNECTION = 2
COULD_BE_EMPTY_OR_SLOW = 3
file_id = 0

PORT = 80
HOST = '127.0.0.1'

class MySocketWrapper():

	def __init__(self, socket):
		self.socket = socket
		self.buff_size = 1024 * 32
		self.buff_size = 1
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
		self.sentHeaders = False
		self.filename = ""
		self.outputHeaders = bytes()
		self.to_send = bytes()
		self.flag_for_uploaded_file = 0

	def parse_first_line(self, line):
		try:
			first_line_split = line.split(" ")
			self.method = first_line_split[0]
			self.url = first_line_split[1]
			self.normalizeUrl()
			self.qs = parse_qs(urlparse("http://" + HOST + self.url).query)
			self.protocol = first_line_split[2]
		except Exception as e:
			print("Problem in parsing the first line:\n\t{0}".format(e))
			print("First line: {0}".format(line))
			#print("45:" + str(e))
			#print("Data for exception: " + str(first_line_split))
			return KILL_CONNECTION

	def getHeaders(self, headers):
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
				print("69: " + str(e))
				continue

	def read(self):
		print("Im in read!")
		self.i = 0
		try:
			while True:
				data_received = self.socket.recv(self.buff_size)
				if not data_received:
					break
				self.data += data_received
		except Exception as e:
			print("80: {0}".format(e))
			if e.errno == 11:
				return COULD_BE_EMPTY_OR_SLOW
			else:
				self.close()
				return KILL_CONNECTION

		# if self.method == "POST":

		# 	try:
		# 		filename = self.qs["filename"][0]
		# 	except Exception as e:
		# 		self.socket.send(bytes("Туй трябва да има filename като GET param", "utf-8"))
		# 		self.close()
		# 		return KILL_CONNECTION

		# 	try:
		# 		data_to_write = data_received.split(b"\r\n\r\n")[1]
		# 	except Exception as e:
		# 		data_to_write = data_received

		# 	if not self.fileHandler:
		# 		file_path = master_root + "/uploads/" + filename

		# 		if os.path.isfile(file_path):
		# 			global file_id
		# 			file_id += 1
		# 			files_splitted = file_path.rsplit(".", 1)
		# 			file_path = files_splitted[0] + "({0})".format(file_id) + "." + files_splitted[1]

		# 		self.fileHandler = open(file_path, "wb")

		# 	try:
		# 		bytes_written = self.fileHandler.write(data_to_write)
		# 	except Exception as e:
		# 		print(e)

		return CLOSE_CONNECTION	


	def write(self):
		print("Im in write!")
		if self.url is "":
			headers_bytes = self.data.split(b"\r\n\r\n")[0]
			try:
				headers = headers_bytes.decode("utf-8")
			except Exception as e:
				print(e)
				self.close()
				return KILL_CONNECTION

			header_lines = headers.split("\n")
			
			result = self.parse_first_line(header_lines[0])
			if result == KILL_CONNECTION:
				return KILL_CONNECTION


			self.getHeaders(header_lines[1:])		

		print("Im in get!")
		if self.method == "GET":
			if self.fileHandler is None:
				
				method_or_string, first_line = getFileNameOnDisk(self.url)
				
				if type(method_or_string) is str:
					self.url = method_or_string
				else:
					self.url = method_or_string()

				self.setHeaders(first_line)
				self.setHeaders(util.curr_date())
				self.setHeaders(util.type_to_expire(self.url))
				self.endHeaders()

				try:
					self.fileHandler = open(master_root + self.url, "rb")
				except Exception as e:
					print("157: {0}".format(e))
					self.close()
					return CLOSE_CONNECTION

			try:
				while True:
					data_to_send = self.fileHandler.read(self.buff_size)
					self.to_send += data_to_send
					if not data_to_send:
						break
			except Exception as e:
				print("167: {0}".format(e))
				self.close()			
				return CLOSE_CONNECTION
				
			try:
				if not self.sentHeaders:
					self.socket.send(self.outputHeaders)
					self.sentHeaders = True

				self.socket.send(self.to_send)
			except Exception as e:
				print("Unable to send data from file to socket!\n\t{0}".format(e))
				self.close()
				return CLOSE_CONNECTION
			
			return 1

		else:
			try:
				self.socket.send("We dont support this!".encode("utf-8"))
				self.close()
			except Exception as e:
				self.close()
				return CLOSE_CONNECTION
			self.close()
			return CLOSE_CONNECTION


	def fileno(self):
		return self.socket.fileno()

	def normalizeUrl(self):
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

	def setHeaders(self, header):
		self.outputHeaders += header + b"\r\n"

	def endHeaders(self):
		self.outputHeaders += b"\r\n"

	def __str__(self):
		return "Socket with fd: {0}".format(self.fileno())