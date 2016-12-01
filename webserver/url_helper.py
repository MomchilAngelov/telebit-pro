import os
from os import path
import sys

master_root = os.getcwd()
master_root += "/"
master_root += sys.argv[1]

STATICS = []

static_dir = master_root + "/static/"

for dirname, dirnames, filenames in os.walk(static_dir):
	for filename in filenames:
		full_filename = os.path.normpath(dirname) + "/" + filename
		common = "/" + os.path.relpath(full_filename, master_root)
		tup = (common, common)
		STATICS.append(tup)