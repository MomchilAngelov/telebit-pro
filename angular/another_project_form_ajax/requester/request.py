import tornado.ioloop
import tornado.web

from urllib import parse, request

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

def make_app():
	return tornado.web.Application([
		(r"/(.*)/", MainHandler),
	])

if __name__ == "__main__":
	app = make_app()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()
