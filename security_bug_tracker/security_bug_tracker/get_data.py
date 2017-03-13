import urllib.request
import platform, sys

import argparse

from bs4 import BeautifulSoup

origin = "https://security-tracker.debian.org"
site_with_packages = "https://security-tracker.debian.org/tracker/status/release/stable"
if len(sys.argv) == 3:
	DEBUG = True
else:
	DEBUG = False

def getOs():
	if DEBUG:
		print(platform.release())
		print(platform.platform())
		print(platform.system())
		print(platform.version())
		print(platform.dist())
		print(platform.linux_distribution())

	return "jessie"

def getUrgency():
	urgency = sys.argv[1]
	return_urgency = set()
	if "h" in urgency:
		return_urgency.add("high")
	if "m" in urgency:
		return_urgency.add("medium")
	if "u" in urgency:
		return_urgency.add("not yet assigned")
	if "l" in urgency:
		return_urgency.add("low")

	if DEBUG:
		print("Urgency: ")
		print(return_urgency)
	
	return return_urgency

def getPackages():
	packages = []

	with open("packages/packages.txt", "r") as f:
		for package in f:
			packages.append(package.strip())

	if DEBUG:
		print("Packges: ")
		print(packages)
	return packages

def openWebsiteWithBS(website):
	return BeautifulSoup(urllib.request.urlopen(website).read(), "lxml")

def urgency_level(row, urgency):
	urg = row.find_all('td')[2].string.replace("*", "")
	if urg in urgency:
		return urg
	else:
		return None 

def getSourcePackageAndItsChildren(website, package, table_part):
	links = []
	
	for tr in website.find_all('table')[table_part].find_all('tr'):
		if tr.find('td'):
			if tr.find('td'):
				links.append(tr.find('td'))

	could_be_multiple = False

	part_of_table = []
	for link in links:
		a = link.find('a')

		if (a is not None) and ("/tracker/source-package/" + package in a["href"]):
			could_be_multiple = True
			part_of_table.append(a.parent.parent)

		elif (a is None or a["href"] == "/tracker/source-package/") and could_be_multiple: 
			part_of_table.append(link.parent)

		elif could_be_multiple:
			break

	return part_of_table

def getAllBugs(website, urgency_level_specified, packages):
	dict_package_to_bugs = {}
	for package in packages:
		dict_package_to_bugs[package] = {}

		mini_table = getSourcePackageAndItsChildren(website, package, 0)
		for row in mini_table:
			urgency_level_returned = urgency_level(row, urgency_level_specified)
			if urgency_level_returned is not None:
				bug_link = row.find_all('td')[1].find('a')['href']
				dict_package_to_bugs[package][bug_link] = {}
				dict_package_to_bugs[package][bug_link]["urgency"] = urgency_level_returned

	return dict_package_to_bugs

def getOsVulnerabillity(table, dist):
	for row in table:
		if row.find('td'):
			columns = row.find_all('td')
			if dist in (dist.strip() for dist in columns[1].string.split(",")):
				if 'vulnerable' in columns[3].string.split(","):
					return True
				else:
					return False


os = getOs()
urgency_level_specified = getUrgency()
packages = getPackages()

website = openWebsiteWithBS(site_with_packages)

package_to_links = getAllBugs(website = website, urgency_level_specified = urgency_level_specified, packages = packages)

for package_name, bug_hash in package_to_links.items():

	for bug in bug_hash:
		bug_hash[bug] = {}
		print("Parsing data for bug", bug.split("/")[-1], "found in package", package_name)

		website = openWebsiteWithBS(origin + bug)
		part_of_table = getSourcePackageAndItsChildren(website, package_name, 1)

		is_vulnerable = getOsVulnerabillity(part_of_table, os)
		bug_hash[bug]["vulnerable"] = is_vulnerable
		bug_hash[bug]["os"] = os
		print("Your OS '{0}' is {1} to {2}".format(os, "vulnerable" if is_vulnerable else "not vulnerable", origin+bug))