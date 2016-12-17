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
SPECIAL_CONDITION = 4
file_id = 0
DEBUG = 0

if len(sys.argv) == 4 and sys.argv[3] == 'DEBUG':
	DEBUG = 1

PORT = int(sys.argv[2])
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
		self.is_file_read = False
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
		try:
			while True:
				data_received = self.socket.recv(self.buff_size)
				if not data_received:
					return self.prepare_for_write()
				self.data += data_received
				if b"\r\n\r\n" in self.data:
					return self.prepare_for_write()
		except Exception as e:
			if e.errno == 11:
				# Resource temporary unavailable
				# Това е еррора, ако трябва да блокне, но не блоква

				return COULD_BE_EMPTY_OR_SLOW
			else:
				if DEBUG:
					print("read function: {0}".format(e))
				self.close()
				return KILL_CONNECTION

	def prepare_for_write(self):
		if self.url is "":
			if not self.data:
				print("The socket gave no information and i can't read from it -> KILL IT - prepare for write")
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

		return CLOSE_CONNECTION

	def open_file(self):
		method_or_string, first_line = getFileNameOnDisk(self.url)
				
		if type(method_or_string) is str:
			self.url = method_or_string
		else:
			self.url = method_or_string()

		self.setHeaders(first_line)
		self.setHeaders(util.curr_date())
		self.setHeaders(util.type_to_expire(self.url))
		self.endHeaders()

		if DEBUG:
			print(self.method + " " + self.url + " " + first_line.split(b" ")[1].decode("utf-8"))

		try:
			self.fileHandler = open(master_root + self.url, "rb")
			if DEBUG:
				print("Отваряме файла...")
		except Exception as e:
			print("Unable to open the file i should read to give him the (html or etc.): {0}".format(e))
			self.close()
			return CLOSE_CONNECTION

		return 1

	def read_file(self):
		try:
			if DEBUG:
				print("Четене от файла {0}".format(self.url))

			while True:
				data_to_send = self.fileHandler.read(self.buff_size_file_read)
				if DEBUG:
					print("I read {0} bytes\ntotal read: {1}".format(len(data_to_send), len(self.to_send)))
				self.to_send += data_to_send
				if len(data_to_send) < self.buff_size_file_read:
					self.is_file_read = True
					return 1

		except Exception as e:
			print("Problem with reading the file (html or etc.): {0}".format(e))
			self.close()			
			return CLOSE_CONNECTION

	def write(self):
		if self.url is "":
			self.prepare_for_write()

		if self.method == "GET":			
			if self.fileHandler is None:
				result = self.open_file()
				if result == CLOSE_CONNECTION:
					self.close()
					return result

			if not self.is_file_read:
				result = self.read_file()
				if result != 1:
					self.close()
					return result
				
			if not self.sentHeaders:
				result = self.send_data_to_socket(self.outputHeaders, len(self.outputHeaders))
				if result == SPECIAL_CONDITION:
					self.sentHeaders = True
					self.to_where = 0
				
				elif result == 1:
					return result
				
				else:
					self.close()
					return result

			result = self.send_data_to_socket(self.to_send, len(self.to_send))
			if result == 1:
				return 1

			elif result == SPECIAL_CONDITION:
				self.close()
				return CLOSE_CONNECTION

			else:	
				self.close()
				return result
					
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

	def send_data_to_socket(self, data_to_send, size_of_data):
		while self.to_where != size_of_data:
			try:
				wrote_bytes = self.socket.send(data_to_send[self.to_where:self.to_where+self.buff_size])
			except Exception as e:
				if e.errno == 11:
					# we should continue to write, the buffer of the OS is full tho 
					return 1

				if e.errno == 32:
					print("The Client has closed the connection prematurely! - send_data_to_socket function")
					print(e)
					self.close()
					return CLOSE_CONNECTION

				print("Unable to send the file to the socket: " + str(e) + "send_data_to_socket function")
				self.close()
				return CLOSE_CONNECTION

			self.to_where += wrote_bytes

		return SPECIAL_CONDITION