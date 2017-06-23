#!/usr/bin/env python3
import error_handling_library.test_hooks as ut
from libs.logger import Logger

LOGGER = Logger()
ut.init( logger = LOGGER )

import time, os, argparse, sys, requests, gevent, grequests

from gevent import socket, Timeout 

from libs.dataGiver import DataGiver
from libs.outputDataIntoDict import Outputter
from libs.resolver import Resolver

parser = argparse.ArgumentParser(description = """Ping some ips and hosts ;)""")
parser.add_argument("-o", "--output", help="Output format", type = str, choices=["json", "xml"], default="json")
parser.add_argument("-c", "--configure", help="Give the ip json file", type = str, default = False)
parser.add_argument("-s", "--stats", help="Give some statistics on the screen!", action = "store_true", default = False)
parser.add_argument("-d", "--directory", help="Put the output in written directory. WIll be created if not there.", type = str, default = False)

args = parser.parse_args()

STATS = args.stats

versionNumber = "3.0"
applicationName = "Momo's Pinger"

defaultSearchFolder = "/etc/tbmon/defaultHTMLJSON"
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

	def __init__(self, item, outputter):
		self.address = item['address']
		self.requests_count = item['requests_count']
		self.request_timeout = item['request_timeout']
		self.idx = item['idx']
		self.application_name_human_name = item.get('application_name_human_name', None)
		self.application_name = item.get('application_name', None)
		self.expected_response_code = item.get('expected_response_code', None)
		self.expected_headers = item.get('expected_headers', None)
		self.expected_response_bodies = item.get('expected_response_bodies', None)
		self.basicauthUsername = item.get('username', None)
		self.basicauthPassword = item.get('password', None)
		self.triggerWrappers = item.get('items', None)
		self.dictAttackTestConditions = item.get('password_dict_test', None)
		
		self.outputter = outputter

		ut.checkType(type(item['address']), type(''))
		ut.checkType(type(item['requests_count']), type(1))
		ut.checkType(type(item['request_timeout']), type(1), type(0.5))
		ut.checkType(type(item['idx']), type(''))
		ut.checkType(type(self.expected_headers), type(None), type([]))
		ut.checkType(type(self.expected_response_code), type(None), type([]))

		self.normalizeInput()
		self.ping()

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

	def ping(self):
		global OPENED_HTTP_REQUESTS

		self.data = {}
		self.data['items'] = self.triggerWrappers
		self.data['idx'] = self.idx
		self.data['timestamp'] = int(time.time())
		self.data['type'] = 'float'
		self.data['name'] = self.address
		self.data['units'] = '%'
		self.data['application_name_human_name'] = self.application_name_human_name
		self.data['application_name'] = self.application_name
		self.credentials = None
		self.method_changed = False
		self.method = 'HEAD'
		self.failedRequests = 0


		should_block_http_requests()
		OPENED_HTTP_REQUESTS += 1

		k = 0
		while k < self.requests_count:

			try:
				r = requests.request(method = self.method, url = self.address, auth = self.credentials, allow_redirects = True, timeout = self.request_timeout, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'})
			except requests.TooManyRedirects as e:
				LOGGER.log(str(e))
				self.failedRequests += 1
				k += 1
				continue

			except Exception as e:
				k += 1
				self.failedRequests += 1
				continue

			if r.status_code == 405 and not self.method_changed:
				method_changed = True
				self.method = 'GET'
				continue
				

			if r.status_code == 401 and not self.credentials:
				if self.username:
					self.credentials = (self.username, self.password)
					continue
				else:
					self.failedRequests = self.requests_count
					break


			if self.expected_response_code and self.expected_headers:
			
				self.expected_headers = set(self.expected_headers)
				if not (self.expected_headers.issubset(set(r.headers)) and r.status_code in self.expected_response_code):
					self.failedRequests = self.requests_count
					break
			
			elif self.expected_response_code:
			
				if not r.status_code in self.expected_response_code:
					self.failedRequests = self.requests_count
					break
			elif self.expected_headers:
				self.expected_headers = set(self.expected_headers)
				
				if not self.expected_headers.issubset(set(r.headers)):
					self.failedRequests = self.requests_count
					break

			k += 1

		
		OPENED_HTTP_REQUESTS -= 1
		#If all the requests hit a timeout
		self.data['value'] = 100 - (1 - (self.failedRequests / self.requests_count)) * 100

		self.outputter.appendItemToOutputterHTML(self.data)

def main():
	if STATS:
		stater = Statistics()
		mark = gevent.spawn(stater.printData)

	data_giver = DataGiver()
	outputter = Outputter(versionNumber = versionNumber, applicationName = applicationName)
	resolver = Resolver(outputter = outputter, class_of_pinger = HtmlPinger, should_resolve = False)

	data = gevent.spawn(data_giver.getDataFromFile, searchFolder, resolver)
	data.link_exception(ut.greenletException)
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
