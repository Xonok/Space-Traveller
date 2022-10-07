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

import http.server,os,ssl,json,hashlib,random,sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from server import io,user,map,player,market


def dice(amount,sides):
	sum = 0
	for i in range(amount):
		sum += random.randint(1,sides)
	return sum

class MyHandler(BaseHTTPRequestHandler):
	def check(self,msg,*args):
		for arg in args:
			if not arg in msg:
				self.send_msg(401,"Missing required \""+arg+"\"")
				return False
		return True
	def do_POST(self):
		path = urlparse(self.path).path
		try:
			content_len = int(self.headers.get('Content-Length'))
			data = json.loads(self.rfile.read(content_len))
		except:
			self.send_msg(401,"Invalid JSON data")
			return
		if path == "/login.html":
			if not self.check(data,"command","username","password"):
				return
			command = data["command"]
			username = data["username"]
			password = data["password"]
			if command == "register":
				if user.register(username,password):
					self.send_msg(201,"Success.")
				else:
					self.send_msg(401,"Username already exists.")
			elif command == "login":
				if not user.check_user(username):
					self.send_msg(401,"Username doesn't exist.")
				elif not user.check_pass(username,password):
					self.send_msg(401,"Invalid password.")
				else:
					self.send_msg(200,str(user.make_key(username)))
		elif path == "/nav.html":
			if not self.check(data,"command","key"):
				return
			command = data["command"]
			key = data["key"]
			username = user.check_key(key)
			if not username:
				self.redirect(401,"text/html","login.html")
				return
			player.check(username)
			pdata = player.data[username]
			system = pdata["system"]
			px,py = pdata["position"]
			if command == "move":
				if not self.check(data,"position"):
					return
				prev_x,prev_y = px,py
				px,py = data["position"]
				tile = map.get_tile(system,px,py)
				if "color" not in tile:
					self.send_msg(400,"Can't move there.")
					return
				else:
					diff_x = px-prev_x
					diff_y = prev_y-py
					if abs(diff_x) > abs(diff_y):
						diff_y = 0
					if abs(diff_y) > abs(diff_x):
						diff_x = 0
					diff_x = min(diff_x,1)
					diff_x = max(diff_x,-1)
					diff_y = min(diff_y,1)
					diff_y = max(diff_y,-1)
					delta = str(diff_x)+","+str(diff_y)
					directions = {
						"0,1": 0,
						"1,1": 45,
						"1,0": 90,
						"1,-1": 135,
						"0,-1": 180,
						"-1,-1": 225,
						"-1,0": 270,
						"-1,1":315
					}
					pdata["rotation"] = directions[delta]
					pdata["position"] = (px,py)
			elif command == "gather":
				tile = map.get_tile(system,px,py)
				if "color" in tile:
					if tile["color"] == "#000000":
						print("a")
					elif tile["color"] == "#00bfff":
						res = dice(2,6)
						res = min(pdata["space_available"],res)
						pdata["space_available"] -= res
						player.add_item(pdata["items"],"energy",res)
					elif tile["color"] == "#ff0000":
						res = dice(3,6)
						res = min(pdata["space_available"],res)
						pdata["space_available"] -= res
						player.add_item(pdata["items"],"gas",res)
			elif command == "drop":
				if not self.check(data,"items"):
					return
				items = data["items"]
				for name,amount in items.items():
					pdata["space_available"] += player.remove_item(pdata["items"],name,amount)
			elif command == "dock":
				self.redirect(303,"text/html","trade.html")
				return
			player.write()
			tiles = {}
			vision = 5
			for x in range(px-vision,px+vision+1):
				if x not in tiles:
					tiles[x] = {}
				for y in range(py-vision,py+vision+1):
					tiles[x][y] = map.get_tile(system,x,y)
			buttons = {
				"gather":"initial",
				"drop_all":"none",
				"dock":"none"
			}
			if pdata["space_available"] != pdata["space_total"]:
				buttons["drop_all"] = "initial"
			if market.get(system,px,py):
				buttons["dock"] = "initial"
			msg = {"tiles":tiles,"pdata":pdata,"buttons":buttons}
			self.send_msg(200,json.dumps(msg))
		elif path == "/trade.html":
			if not self.check(data,"command","key"):
				return
			command = data["command"]
			key = data["key"]
			username = user.check_key(key)
			if not username:
				self.redirect(401,"text/html","login.html")
				return
			player.check(username)
			pdata = player.data[username]
			system = pdata["system"]
			px,py = pdata["position"]
			tile_market = market.get(system,px,py)
			if not tile_market:
				self.redirect(303,"text/html","nav.html")
				return
			if command == "trade-goods":
				if not self.check(data,"buy","sell"):
					return
				market.trade(pdata,data,tile_market)
			msg = {"pdata":pdata,"market":tile_market}
			self.send_msg(200,json.dumps(msg))
	def do_GET(self):
		url_parts = urlparse(self.path)
		path = url_parts.path
		if path.startswith('/'):
			path = path[1:]
		file = os.path.join(io.cwd,*path.split('/'))
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
				self.wfile.write(io.get_file_data("login.html"))
			else:
				self.send_response(404)
				self.send_header("Access-Control-Allow-Origin","*")
				self.end_headers()
		elif type == ".js":
			self.send_file(200,"text/javascript",file)
		elif type == ".css":
			self.send_file(200,"text/css",file)
		elif type == ".png":
			self.send_file(200,"image/png",file)
		elif type == ".html":
			self.send_file(200,"text/html",file)
	def send_msg(self,code,msg):
		self.send_response(code)
		self.send_header("Content-Type","text/plain")
		self.send_header("Access-Control-Allow-Origin","*")
		self.end_headers()
		self.wfile.write(bytes(msg,"utf-8"))
	def send_file(self,code,type,path):
		self.send_response(code)
		self.send_header("Content-Type",type)
		self.send_header("Access-Control-Allow-Origin","*")
		self.end_headers()
		self.wfile.write(io.get_file_data(path))
	def redirect(self,code,type,target):
		self.send_response(code)
		self.send_header("Content-Type",type)
		self.send_header("Access-Control-Allow-Origin","*")
		self.send_header("Location",target)
		self.end_headers()

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(".ssh/certificate.pem",".ssh/key.pem")
httpd = http.server.HTTPServer(("", 443), MyHandler)
httpd.socket = context.wrap_socket(httpd.socket,server_side=True)
httpd.serve_forever()
