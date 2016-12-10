import sys
import os
import os.path
import urllib.parse
from urllib.parse import urlparse, parse_qs
import select
import socket
import datetime
import math
import time
import errno

from pathing_string import *
import util

CLOSE_CONNECTION = 0
KILL_CONNECTION = 2
COULD_BE_EMPTY_OR_SLOW = 3
file_id = 0

PORT = 80
HOST = ''

class MySocketWrapper():

	def __init__(self, socket):
		self.socket = socket
		self.buff_size = 1024 * 64
		self.buff_size_file_read = 1024*256
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
		split_line = line.split(" ")
		if len(split_line) != 3:
			print("Prolem parsing the header line...")
			#print(self.data)
			return KILL_CONNECTION
			
		self.method, self.url, self.protocol = split_line
		self.normalizeUrl()
		self.qs = parse_qs(urlparse("http://" + HOST + self.url).query)

		return 1

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
				print("Problem in the headers parsing: " + str(e))
				continue

	def read(self):
		#print("Im in read!")
		try:
			while True:
				data_received = self.socket.recv(self.buff_size)
				if not data_received:
					break
				self.data += data_received
		except Exception as e:
			#print("80: {0}".format(e))
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
		#print("Im in write!")
		if self.url is "":
			if not self.data:
				print("The socket gave no information and i can't read from it -> KILL IT")
				return KILL_CONNECTION

			headers_bytes = self.data.split(b"\r\n\r\n")[0]
			try:
				headers = headers_bytes.decode("utf-8")
			except Exception as e:
				print("Trying to decode the header bytes (i think they should be utf-8 so i can know what it says?)" + str(e))
				self.close()
				return KILL_CONNECTION

			header_lines = headers.split("\n")
			
			result = self.parse_first_line(header_lines[0])

			if result == KILL_CONNECTION:
				return KILL_CONNECTION


			self.getHeaders(header_lines[1:])		

		#print("Im in get!")
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
					#print("Отваряме файла...")
				except Exception as e:
					print("Unable to open the file i should read to give him the (html or etc.): {0}".format(e))
					self.close()
					return CLOSE_CONNECTION

			if self.to_where == 0:
				try:
					#print("Четене от файла {0}".format(self.url))
					self.date = datetime.datetime.now()
					while True:
						data_to_send = self.fileHandler.read(self.buff_size_file_read)
						self.to_send += data_to_send
						#print("Изчетени байтове: {0}".format(len(self.to_send)))
						if len(data_to_send) < self.buff_size_file_read:
							#print("Отнето време за изчитане на файла:\n\t", end="")
							#print(datetime.datetime.now()-self.date)
							break
				except Exception as e:
					print("Problem with reading the file (html or etc.): {0}".format(e))
					self.close()			
					return CLOSE_CONNECTION
			try:
				if not self.sentHeaders:
					self.socket.send(self.outputHeaders)
					self.sentHeaders = True

				all_bytes = len(self.to_send)
				while self.to_where != all_bytes:
					try:
						read_bytes = self.socket.send(self.to_send[self.to_where:self.to_where+self.buff_size_file_read])
					except Exception as e:
						if e.errno == 11:
							return 1

						if e.errno == 32:
							print("The Client has closed the connection prematurely!")
							print(e)
							self.close()
							return CLOSE_CONNECTION

						print("Unable to send the file to the socket: " + str(e))
						self.close()
						return CLOSE_CONNECTION

					#print("Изпратени байтове: {0}-{1}/{2}".format(self.to_where, self.to_where+self.buff_size, all_bytes))
					self.to_where += read_bytes
					
			except Exception as e:
				print("Unable to send data from file to socket!\n\t{0}".format(e))
				self.close()
				return CLOSE_CONNECTION
			
			self.close()
			return CLOSE_CONNECTION

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
			pass

		try:
			self.my_uploaded_file.close()
		except Exception as e:
			pass
		
		try:
			self.socket.close()
		except Exception as e:
			pass

	def setHeaders(self, header):
		self.outputHeaders += header + b"\r\n"

	def endHeaders(self):
		self.outputHeaders += b"\r\n"

	def __str__(self):
		return "Socket with fd: {0}".format(self.fileno())