import fnmatch
import os
import glob

my_glob_result = glob.glob("test_Data/input.json")
for python_file in my_glob_result:
	print(python_file)