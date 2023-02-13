import http.server,os,ssl,json,copy,hashlib,base64,time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from server import io,user,player,func,items,factory,ship,defs,structure,map,quest,error,chat,battle,hive,ark,loot,gathering,build

class MyHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		path = urlparse(self.path).path
		try:
			content_len = int(self.headers.get('Content-Length'))
			data = json.loads(self.rfile.read(content_len))
		except:
			raise error.User("Invalid JSON data.")
		try:
			if path == "/login.html":
				user.handle_login(self,data)
			self.check(data,"command","key")
			username = user.check_key(data["key"])
			command = data["command"]
			if path == "/chat.html":
				chat.handle_command(self,data,username)
				raise error.User("Unknown command for chat page: "+command)
			pdata = defs.players.get(username)
			if "ship" in data:
				if ship.get(data["ship"])["owner"] != username: raise error.User("You don't own that ship.")
				pdata["ship"] = data["ship"]
			pship = ship.get(pdata.ship())
			pitems = pship.get_items()
			psystem = pship.get_system()
			stiles = map.tilemap(psystem)
			px,py = pship.get_coords()
			tstructure = structure.get(psystem,px,py)
			pbattle = battle.get(pship)
			if pbattle and path != "/battle.html":
				raise error.Battle()
			if not pbattle and path == "/battle.html":
				raise error.Page()
			if path == "/nav.html":
				if command == "move":
					map.move(self,data,pdata)
				elif command == "gather":
					gathering.gather(pship)
				elif command == "drop":
					items.drop(self,data,pitems)
				elif command == "use_item":
					items.use(self,data,pdata)
				elif command == "ship-trade":
					self.check(data,"target","items")
					ship.trade(self,data,pdata)
				elif command == "jump":
					self.check(data,"wormhole")
					map.jump(self,data,pdata)
				elif command == "start-battle":
					self.check(data,"target")
					battle.start_battle(data,pdata)
				elif command == "guard":
					self.check(data,"ship")
					ship.guard(data,pdata)
				elif command == "follow":
					self.check(data,"ship")
					ship.follow(data,pdata)
				elif command == "homeworld-return":
					hive.use_homeworld_return(data,pdata)
				elif command == "take-loot":
					self.check(data,"items")
					loot.take(data,pdata)
				elif command == "pack-station":
					structure.pick_up(pship)
				elif command == "ship-rename":
					self.check(data,"name")
					pship.rename(data["name"])
				ark.tick()
				px,py = pship.get_coords()
				psystem = pship.get_system()
				otiles = map.objmap(psystem)
				gathering.update_resources(otiles,px,py)
				tstructure = structure.get(psystem,px,py)
				structinfo = {}
				if tstructure:
					structinfo = {
						"name": tstructure["name"],
						"type": tstructure["type"],
						"owner": tstructure["owner"],
						"image": defs.ship_types[tstructure["ship"]]["img"]
					}
				#pship = ship.get(pdata.ship())
				pship.get_space()
				pship.save()
				pships = ship.player_ships(pdata["name"])
				vision = 3
				ship_defs = {}
				for data in pships.values():
					ship_defs[data["type"]] = defs.ship_types[data["type"]]
					pgear = data.get_gear()
					if "highpower_scanner" in pgear:
						vision += 2
				tiles = map.get_tiles(psystem,px,py,vision)
				tile = map.get_tile(psystem,px,py,username)
				buttons = {
					"gather": "initial",
					"loot": "initial" if "items" in tile else "none",
					"drop_all": "initial" if len(pitems) else "none",
				}
				idata = items.player_itemdata(pdata)
				hwr = hive.hwr_info(pship)
				constellation = defs.constellation_of[pship["pos"]["system"]]
				msg = {"vision":vision,"tiles":tiles,"tile":tile,"pdata":pdata,"ships":pships,"buttons":buttons,"structure":structinfo,"idata":idata,"hwr":hwr,"constellation":constellation,"ship_defs":ship_defs}
				self.send_msg(200,json.dumps(msg))
			elif path == "/trade.html":
				if not tstructure:
					raise error.Page()
				tstructure.tick()
				tstructure.make_ships()
				if command == "trade-goods":
					self.check(data,"buy","sell")
					tstructure.trade(pdata,data)
				elif command == "transfer-goods":
					self.check(data,"take","give","take_gear","give_gear")
					tstructure.transfer(pdata,data)
				elif command == "equip":
					self.check(data,"ship-on","ship-off","station-on","station-off")
					tstructure.equip(data)
					pship.equip(data)
				elif command == "quest-accept":
					self.check(data,"quest-id")
					quest.accept(self,data,pdata)
				elif command == "quest-cancel":
					self.check(data,"quest-id")
					quest.cancel(self,data,pdata)
				elif command == "quest-submit":
					self.check(data,"quest-id")
					quest.submit(self,data,pdata)
				elif command == "start-build":
					self.check(data,"blueprint")
					build.start(data,pdata,tstructure)
				elif command == "equip-blueprint":
					self.check(data,"blueprint")
					build.equip_blueprint(data,pdata,tstructure,pship)
				prices = tstructure.get_prices()
				itypes = {}
				for item in prices.keys():
					itype = items.type(item)
					if itype not in itypes:
						itypes[itype] = []
					itypes[itype].append(item)
				quests = tstructure["quests"]
				quest_defs = {}
				for q in quests:
					quest_defs[q] = defs.quests[q]
				idata = items.structure_itemdata(tstructure,pdata) | items.player_itemdata(pdata) | items.itemlist_data(prices.keys())
				pships = map.get_player_ships(pdata)
				station_def = defs.ship_types[tstructure["ship"]]
				bp_info = build.get_bp_info(tstructure)
				ship_defs = {}
				for data in pships.values():
					ship_defs[data["type"]] = defs.ship_types[data["type"]]
				msg = {"pdata":pdata,"ship":pship,"ships":pships,"structure":tstructure,"itypes":itypes,"quests":quest_defs,"idata":idata,"prices":prices,"station_def":station_def,"bp_info":bp_info,"ship_defs":ship_defs}
				self.send_msg(200,json.dumps(msg))
			elif path == "/battle.html":
				if command == "attack":
					self.check(data,"rounds")
					battle.attack(pdata,data)
				elif command == "retreat":
					battle.retreat(pdata)
				allies = battle.allies(pdata)
				enemies = battle.enemies(pdata)
				ally_weapons = battle.weapons(allies)
				enemy_weapons = battle.weapons(enemies)
				msg = {"pdata":pdata,"battle":pbattle,"allies":allies,"enemies":enemies,"ally_weapons":ally_weapons,"enemy_weapons":enemy_weapons}
				self.send_msg(200,json.dumps(msg))
			elif path == "/quests.html":
				quest_defs = {}
				for q in pdata["quests"].keys():
					quest_defs[q] = defs.quests[q]
				msg = {"pdata":pdata,"quests":quest_defs}
				self.send_msg(200,json.dumps(msg))
			elif path == "/items.html":
				udata = None
				if command == "userdata-update":
					self.check(data,"data")
					io.write2("userdata",pdata["name"],data["data"])
					udata = data["data"]
				if not udata:
					try:
						udata = io.read2("userdata",pdata["name"])
					except Exception as e:
						print(e)
						udata = {}
				msg = {"data":udata}
				self.send_msg(200,json.dumps(msg))
		except error.Auth as e:
			self.redirect(303,"text/html","login.html")
		except error.Page as e:
			self.redirect(303,"text/html","nav.html")
		except error.Battle as e:
			self.redirect(303,"text/html","battle.html")
		except error.User as e:
			self.send_msg(400,str(e))
		except error.Fine as e:
			return
		except Exception as e:
			io.clear_writes()
			self.send_msg(500,"Server error")
			raise
	def do_GET(self):
		self.protocol_version = "HTTP/1.1"
		url_parts = urlparse(self.path)
		path = url_parts.path
		if path.startswith('/'):
			path = path[1:]
		if path == "chat_async":
			chat.get(self)
			return
		file = os.path.join(io.cwd,*path.split('/'))
		_,ftype = os.path.splitext(path)
		if path == '' or not os.path.exists(file):
			if ftype == ".html" or ftype == '' or path == '':
				self.redirect(302,"text/html","/login.html")
			else:
				self.response(404,"text/plain")
		elif ftype == ".js":
			self.send_file(200,"text/javascript",file)
		elif ftype == ".css":
			self.send_file(200,"text/css",file)
		elif ftype == ".png":
			self.send_file(200,"image/png",file)
		elif ftype == ".html":
			print(path)
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
		#self.send_header("Content-Length",0)
		self.wfile.write(bytes(msg,"utf-8"))
	def send_file(self,code,type,path):
		self.response(code,type)
		data = io.get_file_data(path)
		#self.send_header("Content-Length",len(data))
		self.wfile.write(data)
	def redirect(self,code,type,target):
		#self.send_header("Content-Length",0)
		self.response(code,type,"Location",target)
	def check(self,msg,*args):
		for arg in args:
			if not arg in msg:
				raise error.User("Missing required \""+arg+"\"")

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(".ssh/certificate.pem",".ssh/key.pem")
httpd = http.server.ThreadingHTTPServer(("", 443), MyHandler)
httpd.socket = context.wrap_socket(httpd.socket,server_side=True)
httpd.serve_forever()
