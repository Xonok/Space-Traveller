import http.server,os,ssl,json,copy
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from server import io,user,player,func,pop,station,items,factory,ship,defs,structure

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
			user.handle_login(self,data)
			return
		if not self.check(data,"command","key"):
			return
		username = user.check_key(data["key"])
		command = data["command"]
		pdata = defs.players.get(username)
		pitems = pdata.get_items()
		pgear = pdata.get_gear()
		psystem = pdata.get_system()
		stiles = defs.systems[psystem]["tiles"]
		px,py = pdata.get_coords()
		tile0 = stiles.get(px,py)
		tstructure = None
		if "structure" in tile0:
			tstructure = defs.structures[tile0["structure"]]
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
			elif command == "use_item":
				if not self.check(data,"item"):
					return
				used_item = data["item"]
				if pitems.get(used_item):
					factory.use_machine(used_item,pitems,pdata)
					structure.build(used_item,pdata,psystem,px,py)
			tile0 = stiles.get(px,py)
			tstructure = None
			structinfo = {}
			if "structure" in tile0:
				tstructure = defs.structures[tile0["structure"]]
				structinfo = {
					"name": tstructure["name"],
					"type": tstructure["type"],
					"image": defs.ships[tstructure["ship"]]["img"]
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
						tile["structure"] = copy.deepcopy(defs.structures[tile["structure"]])
						tile["structure"]["image"] = defs.ships[tile["structure"]["ship"]]["img"]
			buttons = {
				"gather": "initial",
				"drop_all": "initial" if len(pitems) else "none",
				"dock": "initial" if tstructure else "none"
			}
			pdata.get_space()
			msg = {"tiles":tiles,"pdata":pdata,"buttons":buttons,"structure":structinfo}
			self.send_msg(200,json.dumps(msg))
		elif path == "/trade.html":
			if not tstructure:
				self.redirect(303,"text/html","nav.html")
				return
			#while pop.can_tick(market_pop):
			#	pop.tick(market_pop,tile_market)
			if command == "trade-goods":
				if not self.check(data,"buy","sell"):
					return
				tstructure.trade(pdata,data)
			elif command == "transfer-goods":
				if not self.check(data,"take","give","take_gear","give_gear"):
					return
				tstructure.transfer(pdata,data)
			elif command == "equip":
				if not self.check(data,"ship-on","ship-off","station-on","station-off"):
					return
				tstructure.equip(data)
				pdata.equip(data)
			itypes = {}
			for item in tstructure["market"]["prices"].keys():
				itype = items.type(item)
				if itype not in itypes:
					itypes[itype] = []
				itypes[itype].append(item)
			shipdef = defs.ships[pdata["ship"]]
			msg = {"pdata":pdata,"structure":tstructure,"itypes":itypes,"shipdef":shipdef}
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
