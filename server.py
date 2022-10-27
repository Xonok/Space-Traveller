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

import http.server,os,ssl,json,hashlib,sys,copy
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from server import io,user,map,player,func,pop,station,gear,items,factory,ship,defs

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
					items.init(username)
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
			return
		if not self.check(data,"command","key"):
			return
		command = data["command"]
		key = data["key"]
		username = user.check_key(key)
		if not username:
			self.redirect(302,"text/html","login.html")
			return
		pdata = defs.players.get(username)
		pitems = pdata.get_items()
		pgear = pdata.get_gear()
		psystem = pdata.get_system()
		stiles = defs.systems[psystem]["tiles"]
		px,py = pdata.get_coords()
		tile0 = stiles.get(px,py)
		structure = None
		if "structure" in tile0:
			structure = defs.structures[tile0["structure"]]
		if path == "/nav.html":
			if command == "move":
				if not self.check(data,"position"):
					return
				prev_x,prev_y = px,py
				px,py = data["position"]
				tile = stiles.get(px,py)
				if "terrain" not in tile:
					self.send_msg(400,"Can't move there.")
					return
				else:
					x = px-prev_x
					y = prev_y-py
					if x != 0 or y != 0:
						pdata.move(px,py,func.direction(x,y))
			elif command == "gather":
				if "terrain" in tile0:
					if tile0["terrain"] == "energy":
						pitems.add("energy",min(pdata.get_space(),func.dice(3,6)))
					elif tile0["terrain"] == "nebula":
						pitems.add("gas",min(pdata.get_space(),func.dice(2,6)))
					elif tile0["terrain"] == "asteroids":
						if pgear.get("mining_laser"):
							pitems.add("ore",min(pdata.get_space(),func.dice(2,6)))
			elif command == "drop":
				if not self.check(data,"items"):
					return
				drop_items = data["items"]
				for name,amount in drop_items.items():
					pitems.add(name,-amount)
			elif command == "dock":
				self.redirect(303,"text/html","trade.html")
				return
			elif command == "manage":
				self.redirect(303,"text/html","station.html")
				return
			elif command == "use_item":
				if not self.check(data,"item"):
					return
				machine = data["item"]
				if pitems.get(machine) or pgear.get(machine):
					factory.use_machine(machine,pitems,pdata)
			elif command == "build":
				if pgear.get("station_kit") and not station.get(system,px,py) and not market.get(system,px,py):
					station.add(system,px,py,"img/space-station-sprite-11563508570fss47wldzk.png",username)
					pgear.add("station_kit",-1)
			tile0 = stiles.get(px,py)
			structure = None
			structinfo = {}
			if "structure" in tile0:
				structure = defs.structures[tile0["structure"]]
				structinfo = {
					"name": structure["name"],
					"type": structure["type"],
					"image": structure["image"]
				}
			pdata.save()
			tiles = {}
			vision = 5
			for x in range(px-vision,px+vision+1):
				if x not in tiles:
					tiles[x] = {}
				for y in range(py-vision,py+vision+1):
					tile = copy.deepcopy(stiles.get(x,y))
					tiles[x][y] = tile
					if "structure" in tile:
						tile["structure"] = defs.structures[tile["structure"]]
			buttons = {
				"gather":"initial",
				"drop_all":"none",
				"dock":"none",
				"manage":"none",
				"smelt":"none",
				"brew":"none",
				"build":"none"
			}
			if len(pitems):
				buttons["drop_all"] = "initial"
			if structure:
				if structure["type"] == "planet":
					buttons["dock"] = "initial"
				else:
					buttons["manage"] = "initial"
			if pgear.get("mini_smelter"):
				buttons["smelt"] = "initial"
			if pgear.get("mini_brewery"):
				buttons["brew"] = "initial"
			if pgear.get("station_kit") and not tile_station and not tile_market:
				buttons["build"] = "initial"
			pdata.get_space()
			msg = {"tiles":tiles,"pdata":pdata,"buttons":buttons,"structure":structinfo}
			self.send_msg(200,json.dumps(msg))
		elif path == "/trade.html":
			if not structure:
				self.redirect(303,"text/html","nav.html")
				return
			#while pop.can_tick(market_pop):
			#	pop.tick(market_pop,tile_market)
			if command == "trade-goods":
				if not self.check(data,"buy","sell"):
					return
				structure.trade(pdata,data)
			itypes = {}
			for item in structure["market"]["prices"].keys():
				itype = None
				if item in defs.goods:
					itype = "commodity"
				elif item in defs.gear_types:
					itype = gear.type(item)
				if itype not in itypes:
					itypes[itype] = []
				itypes[itype].append(item)
			msg = {"pdata":pdata,"structure":structure,"itypes":itypes}
			self.send_msg(200,json.dumps(msg))
		elif path == "/station.html":
			if not structure or structure["owner"] != username:
				self.redirect(303,"text/html","nav.html")
				return
			#while station.can_tick(tile_station):
			#	station.tick(tile_station)
			if command == "transfer-goods":
				if not self.check(data,"take","give","take_gear","give_gear"):
					return
				structure.transfer(pdata,data)
			elif command == "equip":
				if not self.check(data,"ship-on","ship-off","station-on","station-off"):
					return
				structure.equip(data)
				pdata.equip(data)
			msg = {"pdata":pdata,"structure":structure}
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
