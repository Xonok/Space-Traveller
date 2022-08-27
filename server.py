#WEB LOGIC
#Respond to get requests for any file in the css, img or js folders.
#Get requests to other folders should return 403(permission denied), except html in main folder.
#Respond to blank request by redirecting to login screen.

#GAME LOGIC(requests)
#Login and register. Keep track of users on disk and in memory.
#Every request requires a session ID. Redirect to login if missing or invalid.
#Requests needed:
#Register/Login - username+password hashed. Return session key if successful, 401 if not.
#Move - session key + coordinates
#Dock - session key + coordinates
#Trade - session key + coordinates + buy dict + sell dict, these dicts are name: amount. Ignore invalid values.
#For Dock and Trade, check location. If no buildings, give "no buildings" page.

#GAME LOGIC(async)
#Every day at 4AM do these things:
#Increase resources on tiles that are not full, up to limit.
#Tick buildings. First calculate if tick can be done, then remove resources, then add.
#If not enough space, throw away cheapest resources first, of those produced this tick.

import http.server,os
from zipfile import ZipFile
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs

cwd = os.path.dirname(os.path.abspath(__file__))

pages = [
"login.html","nav.html","shop.html"
"css/login.css","css/nav.css","css/shop.css",
"js/login.js","js/nav.js","js/shop.js"
]

def get_file_data(path):
	with open(path,"rb") as f:
		return f.read()
class MyHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		print(self.path)
		url_parts = urlparse(self.path)
		path = url_parts.path
		if path.startswith('/'):
			path = path[1:]
		file = os.path.join(cwd,*path.split('/'))
		qs = parse_qs(url_parts.query)
		_,type = os.path.splitext(path)
		if path == '' or not os.path.exists(file):
			if type == ".html" or path == '':
				self.send_response(302)
				self.send_header("Content-Type","text/html")
				self.send_header("Access-Control-Allow-Origin","*")
				target = "/login.html"
				if len(url_parts.query):
					target += "?"+url_parts.query
				self.send_header("Location",target)
				self.end_headers()
				self.wfile.write(get_file_data("login.html"))
			else:
				self.send_response(404)
				self.send_header("Access-Control-Allow-Origin","*")
				self.end_headers()
		elif type == ".js":
			self.send(200,"text/javascript",file)
		elif type == ".css":
			self.send(200,"text/css",file)
		elif type == ".html":
			self.send(200,"text/html",file)
	def send(self,code,type,path):
		self.send_response(code)
		self.send_header("Content-Type",type)
		self.send_header("Access-Control-Allow-Origin","*")
		self.end_headers()
		self.wfile.write(get_file_data(path))

httpd = http.server.HTTPServer(("", 80), MyHandler)
httpd.serve_forever()
