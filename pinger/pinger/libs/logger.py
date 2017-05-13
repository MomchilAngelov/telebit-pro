import os

class Logger():
	def __init__(self, file = "log.txt"):
		self.file = open(file, "a")

	def __del__(self):
		self.file.close()

	def log(self, data):
		self.file.write(data + '\n')
		self.file.flush()