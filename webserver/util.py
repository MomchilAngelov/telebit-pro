from datetime import datetime
from datetime import timedelta

def type_to_expire(relative_file_path):
	try:
		file_extension = relative_file_path.rsplit(".", 1)[1]
	except Exception as e:
		file_extension = "txt"

	if file_extension in ("jpg", "jpeg", "png", "svg"):
		delta = timedelta(days = 365)
	else:
		delta = timedelta(days = 0)	

	expire_time = datetime.now() + delta

	expire_str = "Expire: " + expire_time.strftime("%c")

	return expire_str.encode("utf-8")

def curr_date():
	return ("Date: " + datetime.now().strftime("%c")).encode("utf-8")