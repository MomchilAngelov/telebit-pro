from url_helper import *
import controller

urls = [
	("/", controller.index),
	("/succ/", controller.succ),
	("/ekatte/", controller.ekatte),
	("/ekatte/data/", controller.ekatte_data),
] + STATICS

NOT_FOUND_FILE = "/404.html"

def getFileNameOnDisk(url):
	for url_to_test in urls:
		if url == url_to_test[0]:
			return url_to_test[1], b"HTTP/1.1 200 OK"
	return NOT_FOUND_FILE, b"HTTP/1.1 404 NOT Found"




# strings = []
# strings.append("/data/asadasdadsa/")
# strings.append("/data/1234/")
# strings.append("/data/асд/")
# strings.append("/data/асд123/")
# strings.append("/data/sss/")

# for string in strings:
# 	data = re.search(urls[0], string)
# 	try:
# 		print(data.group('data'))
# 	except Exception as e:
# 		pass