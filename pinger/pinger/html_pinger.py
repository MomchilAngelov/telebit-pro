#!/usr/bin/env python3

import time, os, argparse, sys, requests, gevent, grequests

from gevent import socket, Timeout 

from error_handling_library import test_hooks
from libs.dataGiver import DataGiver
from libs.outputDataIntoDict import Outputter
from libs.Resolver import Resolver

parser = argparse.ArgumentParser(description = """Ping some ips and hosts ;)""")
parser.add_argument("-o", "--output", help="Output format", type = str, choices=["json", "xml"], default="json")
parser.add_argument("-c", "--configure", help="Give the ip json file", type = str, default = False)
parser.add_argument("-s", "--stats", help="Give some statistics on the screen!", action = "store_true", default = False)
parser.add_argument("-d", "--directory", help="Put the output in written directory. WIll be created if not there.", type = str, default = False)

args = parser.parse_args()

STATS = args.stats

versionNumber = "3.0"
applicationName = "Momo's Pinger"

defaultSearchFolder = "test_Data/inputHTML.json"
defaultOutputFolder = "output_data"

searchFolder = args.configure or defaultSearchFolder
outputFolder = args.directory or defaultOutputFolder

OPENED_HTTP_REQUESTS = 0
SHOULD_MAKE_MORE_REQUESTS = 1

MAX_OPENED_HTTP_REUQEST = 400
PROCESS_START_TIME = time.time()


PASSWORDS = {}

def should_block_http_requests():
	global SHOULD_MAKE_MORE_REQUESTS
	global OPENED_HTTP_REQUESTS

	if OPENED_HTTP_REQUESTS > MAX_OPENED_HTTP_REUQEST:
		SHOULD_MAKE_MORE_REQUESTS = 0
	else:
		SHOULD_MAKE_MORE_REQUESTS = 1

	while not SHOULD_MAKE_MORE_REQUESTS:
		gevent.sleep(2)
		if OPENED_HTTP_REQUESTS > MAX_OPENED_HTTP_REUQEST:
			SHOULD_MAKE_MORE_REQUESTS = 0
		else:
			SHOULD_MAKE_MORE_REQUESTS = 1

class Statistics():

	def printData(self):
		while 1:
			print("OPENED_HTTP_REQUESTS: {0}".format(OPENED_HTTP_REQUESTS))
			gevent.sleep(1)

class HtmlPinger():

	def __init__(self, item):
		self.address = item['address']
		self.request_count = item['request_count']
		self.request_interval = item['request_interval']
		self.idx = item['idx']
		self.application_name_human_name = item.get('application_name_human_name', None)
		self.application_name = item.get('application_name', None)
		
		self.expected_response_code = item.get('expected_response_code', None)
		self.expected_headers = item.get('expected_headers', None)

		self.normalizeInput()

	def normalizeInput(self):
		if 'http' not in self.address:
			self.address = 'http://' + self.address

	def getAuthorizationForAddress(self, address):
		global PASSWORDS
		
		if not PASSWORDS:
			PASSWORDS = {line.split("|")[0]: {"name": line.split("|")[1], "password": line.split("|")[2] } for line in open('passwords.txt')}

		if address in PASSWORDS:
			return (PASSWORDS[address]['name'], PASSWORDS[address]['password'])

		return None

	def ping(self, outputter):
		global OPENED_HTTP_REQUESTS

		self.data = {}
		self.data['timestamp'] = int(time.time())
		self.data['type'] = 'boolean'
		self.data['address'] = self.address
		self.data['units'] = None
		self.data['application_name_human_name'] = self.application_name_human_name
		self.data['application_name'] = self.application_name
		self.credentials = None
		self.method_changed = False
		self.method = 'HEAD'

		should_block_http_requests()
		OPENED_HTTP_REQUESTS += 1

		for k in range(self.request_count):

			try:
				r = requests.request(method = self.method, url = self.address, auth = self.credentials, allow_redirects = True, timeout = 1)
			except Exception as e:
				continue
			#Check for 401 and if my guy is there :)

			if r.status_code == 405 and not self.method_changed:
				method_changed = True
				self.method = 'GET'
				continue

			if r.status_code == 401 and not self.credentials:
				self.credentials = self.getAuthorizationForAddress(r.url) or self.getAuthorizationForAddress(self.address)
				if self.credentials:
					continue


			if self.expected_response_code and self.expected_headers:
			
				self.expected_headers = set(self.expected_headers)
				if self.expected_headers.issubset(set(r.headers)) and r.status_code in self.expected_response_code:
					self.data['value'] = 1
				else:
					self.data['value'] = 0
					break
			
			elif self.expected_response_code:
			
				if r.status_code in self.expected_response_code:
					self.data['value'] = 1
				else:
					self.data['value'] = 0
					break
			elif self.expected_headers:
				self.expected_headers = set(self.expected_headers)
				
				if self.expected_headers.issubset(set(r.headers)):
					self.data['value'] = 1
				else:
					self.data['value'] = 0
					break
			else:
				self.data['value'] = 1

			if not self.data['value'] == 1:
				print("For: {0} we got:".format(self.address))
				print("\t", r.status_code)
				print("\t", r.headers)
	
		OPENED_HTTP_REQUESTS -= 1
		#If all the requests hit a timeout
		if not 'value' in self.data:
			self.data['value'] = 0



		outputter.appendItemToOutputterHTML(self.data)

def main():
	if STATS:
		stater = Statistics()
		mark = gevent.spawn(stater.printData)

	data_giver = DataGiver()
	outputter = Outputter(versionNumber = versionNumber, applicationName = applicationName)
	resolver = Resolver(outputter = outputter, class_of_pinger = HtmlPinger, should_resolve = False)

	data = gevent.spawn(data_giver.getDataFromFile, searchFolder, resolver)
	data.join()

	if STATS:
		if not os.path.exists(outputFolder):
			os.makedirs(outputFolder)	
		
		file_if_in_statistics_mode = "{3}/{0}-{1}-output.{2}".format(time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
			applicationName, args.output, outputFolder)

		with open(file_if_in_statistics_mode, "w") as f:
			f.write(outputter.getResult(outputFormat=args.output))
			print(file_if_in_statistics_mode)
	else:
		print(outputter.getResult(outputFormat=args.output))

main()
