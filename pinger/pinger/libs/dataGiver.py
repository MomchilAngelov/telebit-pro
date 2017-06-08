import glob, json, sys, tempfile
import error_handling_library.test_hooks as ut

class DataGiver():

	def __init__(self):
		self.threads = []
		self.domain_to_ips_list = []

	def getDataFromFile(self, file, resolver):
		tmp_arr = []

		files_matching_pattern = glob.glob(file)
		if len(files_matching_pattern) > 1:
			input_json = self.openJSON(self.concatenateFiles(files_matching_pattern))
		else:
			try:
				input_json = self.openJSON(files_matching_pattern[0])
			except Exception as e:
				print("No file found...")
				sys.exit()

		for application_name in input_json["applications"]:
		
			for idx, valueIdx in input_json["applications"][application_name]["items"].items():
				valueIdx['application_name'] = application_name
				valueIdx['application_name_human_name'] = input_json["applications"][application_name]["name"]
				valueIdx['idx'] = idx
				self.domain_to_ips_list.append(valueIdx)
				
		if len(self.domain_to_ips_list):
			resolver.ping_all(self.domain_to_ips_list)		

	def concatenateFiles(self, array_of_files):

		temp = tempfile.TemporaryFile(mode="r+")
		my_json = {}
		my_json["version"] = "3.0"
		my_json["applications"] = {}

		for file in array_of_files:
			with open(file) as f:
				tmp_json = json.load(f)
				for k, v in tmp_json["applications"].items():
					my_json["applications"][k] = v

		json.dump(my_json, temp)

		return temp

	def openJSON(self, file):
		try:
			with open(file, "r") as f:
				result_json = json.load(f)
		except TypeError:
			file.seek(0)
			return_json = json.load(file)
			file.close()
			return return_json
		return result_json
