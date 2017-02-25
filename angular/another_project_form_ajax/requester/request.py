import tornado.ioloop
import tornado.web

from urllib import parse, request
import json, os, shortuuid, sys

class MainHandler(tornado.web.RequestHandler):
	def initialize(self):
		self.set_header("Access-Control-Allow-Origin", "*")

	def get(self, token):
		dict_with_data = {
			"client_id": "4ca47a9bc303b55af5d2",
			"client_secret": "d6ff25620e4461c2655b75f994ba8dff40508430",
			"code": token
		}
		
		endpoint = "https://github.com/login/oauth/access_token"


		if token:
			data = parse.urlencode(dict_with_data).encode()
			my_request = request.Request(endpoint, data = data)
			#print(data)
			my_request.add_header('Accept', 'application/json')
			responce = request.urlopen(my_request)
			#print(responce.read())
			self.write(responce.read())

	def post(self, vals):
		data = json.loads(self.request.body.decode("utf-8"))
		safe_name = shortuuid.uuid()

		try:
			os.system("mkdir /tmp/request/")
		except Exception as e:
			pass

		with open("/tmp/request/"+safe_name, "w") as f:
			f.write(data["text"])

		p = os.popen("git hash-object {0}".format("/tmp/request/"+safe_name),"r")
		res = ""
		while 1:
			line = p.readline()
			if not line:
				break
			res += line

		print("Body of request:", data["text"])
		print("Value of gtihub sha:", res)
		os.system("rm /tmp/request/{0}".format(safe_name))

		self.write(res.encode("utf-8"))

	def options(self, vals):
		self.set_header('Access-Control-Allow-Origin', '*')
		self.clear_header('Content-Type')
		self.clear_header('Content-Length')
		self.set_header('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS');
		self.set_header('Access-Control-Allow-Headers', 'accept, content-type');


def make_app():
	return tornado.web.Application([
		(r"/(.*)/", MainHandler),
		(r"/generate-sha1-github-style/", MainHandler)
	])

if __name__ == "__main__":
	app = make_app()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()
