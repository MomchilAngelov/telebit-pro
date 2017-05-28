import json, tempfile

def openJSON(file):
	try:
		with open(file, "r") as f:
			result_json = json.load(f)
	except TypeError:
		file.seek(0)
		return json.load(file)
	return result_json

temp = tempfile.TemporaryFile(mode="w+")
temp.write('{"momo": 123, "denis": "0/10"}')

my_dict = openJSON(temp)

for k, v in my_dict.items():
	print("my_dict[",k,"] =",v)

temp.close()