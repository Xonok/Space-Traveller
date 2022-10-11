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

import http.server,os,ssl,json,hashlib,sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from server import io,user,map,player,market,func,pop

class MyHandler(BaseHTTPRequestHandler):
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
			pdata = player.check(username)
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
					x = px-prev_x
					y = prev_y-py
					if x != 0 or y != 0:
						pdata["rotation"] = func.direction(x,y)
						pdata["position"] = (px,py)
			elif command == "gather":
				tile = map.get_tile(system,px,py)
				if "color" in tile:
					if tile["color"] == "#000000":
						pass
					elif tile["color"] == "#00bfff":
						player.add_item(pdata,"energy",func.dice(3,6))
					elif tile["color"] == "#ff0000":
						player.add_item(pdata,"gas",func.dice(2,6))
					elif tile["color"] == "#808080":
						if "mining_laser" in pdata["equipment"]:
							player.add_item(pdata,"ore",func.dice(2,6))
			elif command == "drop":
				if not self.check(data,"items"):
					return
				items = data["items"]
				for name,amount in items.items():
					player.remove_item(pdata,name,amount)
			elif command == "dock":
				self.redirect(303,"text/html","trade.html")
				return
			elif command == "smelt":
				if "mini_smelter" in pdata["equipment"]:
					if "ore" in pdata["items"] and pdata["items"]["ore"] >= 6:
						player.remove_item(pdata,"ore",6)
						player.add_item(pdata,"metals",2)
			elif command == "brew":
				if "mini_brewery" in pdata["equipment"]:
					if "gas" in pdata["items"] and pdata["items"]["gas"] >= 4:
						player.remove_item(pdata,"gas",4)
						player.add_item(pdata,"liquor",2)
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
				"dock":"none",
				"smelt":"none",
				"brew":"none"
			}
			if pdata["space_available"] != pdata["space_total"]:
				buttons["drop_all"] = "initial"
			if market.get(system,px,py):
				buttons["dock"] = "initial"
			if "mini_smelter" in pdata["equipment"]:
				buttons["smelt"] = "initial"
			if "mini_brewery" in pdata["equipment"]:
				buttons["brew"] = "initial"
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
			market_pop = tile_market["population"]
			while pop.can_tick(market_pop):
				pop.tick(market_pop,tile_market)
			if not tile_market:
				self.redirect(303,"text/html","nav.html")
				return
			if command == "trade-goods":
				if not self.check(data,"buy","sell"):
					return
				market.trade(pdata,data,tile_market)
			if command == "sell-gear":
				if not self.check(data,"gear"):
					return
				gear = data["gear"]
				if gear in pdata["equipment"] and gear in tile_market["gear"]:
					pdata["equipment"][gear] -= 1
					pdata["credits"] += tile_market["gear"][gear]["buy"]
					tile_market["credits"] -= tile_market["gear"][gear]["buy"]
					pdata["space_available"] += tile_market["gear"][gear]["size"]
					if not pdata["equipment"][gear]:
						del pdata["equipment"][gear]
					player.write()
					market.write(system)
			if command == "buy-gear":
				if not self.check(data,"gear"):
					return
				gear = data["gear"]
				if gear in tile_market["gear"] and pdata["credits"] >= tile_market["gear"][gear]["sell"]:
					if gear not in pdata["equipment"]:
						pdata["equipment"][gear] = 0
					pdata["equipment"][gear] += 1
					pdata["credits"] -= tile_market["gear"][gear]["sell"]
					tile_market["credits"] += tile_market["gear"][gear]["sell"]
					pdata["space_available"] -= tile_market["gear"][gear]["size"]
					player.write()
					market.write(system)
			msg = {"pdata":pdata,"market":tile_market,"population":market_pop}
			self.send_msg(200,json.dumps(msg))
	def do_GET(self):
		url_parts = urlparse(self.path)
		path = url_parts.path
		if path.startswith('/'):
			path = path[1:]
		file = os.path.join(io.cwd,*path.split('/'))
		_,type = os.path.splitext(path)
		if path == '' or not os.path.exists(file):
			if type == ".html" or type == '' or path == '':
				self.redirect(302,"text/html","/login.html")
			else:
				self.response(404,"text/plain")
		elif type == ".js":
			self.send_file(200,"text/javascript",file)
		elif type == ".css":
			self.send_file(200,"text/css",file)
		elif type == ".png":
			self.send_file(200,"image/png",file)
		elif type == ".html":
			self.send_file(200,"text/html",file)
	def response(self,code,type,opt_type=None,opt_data=None):
		self.send_response(code)
		self.send_header("Content-Type",type)
		self.send_header("Access-Control-Allow-Origin","*")
		if opt_type and opt_data:
			self.send_header(opt_type,opt_data)
		self.end_headers()
	def send_msg(self,code,msg):
		self.response(code,"text/plain")
		self.wfile.write(bytes(msg,"utf-8"))
	def send_file(self,code,type,path):
		self.response(code,type)
		self.wfile.write(io.get_file_data(path))
	def redirect(self,code,type,target):
		self.response(code,type,"Location",target)
	def check(self,msg,*args):
		for arg in args:
			if not arg in msg:
				self.send_msg(401,"Missing required \""+arg+"\"")
				return False
		return True

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(".ssh/certificate.pem",".ssh/key.pem")
httpd = http.server.HTTPServer(("", 443), MyHandler)
httpd.socket = context.wrap_socket(httpd.socket,server_side=True)
httpd.serve_forever()
