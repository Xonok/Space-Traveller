import http.server,os,ssl,json,time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from server import io,user,items,ship,defs,structure,map,quest,error,chat,battle,hive,loot,gathering,build,archeology,spawner,stats,Battle

config = {
	"logging": False,
	"text_cache": 10,
	"image_cache": 30
}
try:
	with open("config.json","r") as f:
		config = json.load(f)
except FileNotFoundError as e:
	print("No config found. Creating a new one with default settings.")
except Exception as e:
	raise
with open("config.json","w") as f:
	json.dump(config,f,indent="\t")

class MyHandler(BaseHTTPRequestHandler):
	def __init__(self,*args):
		if not config["logging"]:
			self.log_request = self.no_log
		super().__init__(*args)
	def do_POST(self):
		path = urlparse(self.path).path
		try:
			try:
				content_len = int(self.headers.get('Content-Length'))
				data = json.loads(self.rfile.read(content_len))
			except:
				raise error.User("Invalid JSON data.")
			if path == "/login.html":
				user.handle_login(self,data)
			self.check(data,"command","key")
			username = user.check_key(data["key"])
			command = data["command"]
			if path == "/chat.html":
				chat.handle_command(self,data,username)
				raise error.User("Unknown command for chat page: "+command)
			udata = defs.users.get(username)
			cdata = defs.characters.get(udata["active_character"])
			if not cdata and path != "/characters.html":
				print("No cdata")
				raise error.Char()
			if cdata:
				cname = cdata["name"]
				if "ship" in data:
					if ship.get(data["ship"])["owner"] != cname: raise error.User("You don't own that ship.")
					cdata["ship"] = data["ship"]
				pship = ship.get(cdata.ship())
				pitems = pship.get_items()
				psystem = pship.get_system()
				px,py = pship.get_coords()
				tstructure = structure.get(psystem,px,py)
				pbattle = Battle.get(cdata)
				if pbattle and path != "/battle.html":
					raise error.Battle()
				if not pbattle and path == "/battle.html":
					raise error.Page()
			if path == "/characters.html":
				if command == "make-character":
					self.check(data,"name","starter")
					user.make_character(self,data,udata)
				elif command == "select-character":
					self.check(data,"character")
					user.select_character(self,data,udata)
				pchars = udata["characters"]
				msg = {"characters":pchars,"active_character":udata["active_character"],"starters":defs.starters}
				self.send_msg(200,json.dumps(msg))
			elif path == "/nav.html":
				if command == "move":
					self.check(data,"position")
					map.move2(data,cdata)
				elif command == "gather":
					gathering.gather(pship)
				elif command == "excavate":
					archeology.excavate(data,cdata)
				elif command == "investigate":
					archeology.investigate(self,data,cdata)
				elif command == "drop":
					items.drop(self,data,pship)
				elif command == "use_item":
					items.use(self,data,cdata)
				elif command == "ship-trade":
					self.check(data,"data")
					pship.trade(cdata,data["data"])
				elif command == "jump":
					self.check(data,"wormhole")
					map.jump(self,data,cdata)
				elif command == "start-battle":
					self.check(data,"target")
					Battle.start(cdata,data["target"],self)
				elif command == "guard":
					self.check(data,"ship")
					ship.guard(data,cdata)
				elif command == "follow":
					self.check(data,"ship")
					ship.follow(data,cdata)
				elif command == "homeworld-return":
					hive.use_homeworld_return(data,cdata)
				elif command == "take-loot":
					self.check(data,"items")
					loot.take(data,cdata)
				elif command == "pack-station":
					structure.pick_up(pship)
				elif command == "ship-rename":
					self.check(data,"name")
					pship.rename(data["name"])
				spawner.tick()
				px,py = pship.get_coords()
				psystem = pship.get_system()
				gathering.update_resources(psystem,px,py)
				tstructure = structure.get(psystem,px,py)
				structinfo = {}
				if tstructure:
					structinfo = {
						"name": tstructure["name"],
						"type": tstructure["type"],
						"owner": tstructure["owner"],
						"image": defs.ship_types[tstructure["ship"]]["img"]
					}
				pship.get_space()
				pship.save()
				cdata.save()
				pships = ship.character_ships(cdata["name"])
				vision = 3
				ship_defs = {}
				for data in pships.values():
					ship_defs[data["type"]] = defs.ship_types[data["type"]]
					pgear = data.get_gear()
					if "highpower_scanner" in pgear:
						vision += 2
				tiles = map.get_tiles(psystem,px,py,vision)
				tile = map.get_tile(psystem,px,py,cname)
				buttons = {
					"gather": "initial",
					"excavate": "initial" if archeology.can_excavate(data,cdata) else "none",
					"investigate": "initial" if archeology.can_investigate(data,cdata) else "none",
					"loot": "initial" if "items" in tile else "none",
					"drop_all": "initial" if len(pitems) else "none",
				}
				hwr = hive.hwr_info(cdata)
				constellation = defs.constellation_of[pship["pos"]["system"]]
				idata = items.character_itemdata(cdata)
				starmap = defs.starmap[pship["pos"]["system"]]
				msgs = self.get_messages()
				msg = {"vision":vision,"tiles":tiles,"tile":tile,"cdata":cdata,"ships":pships,"buttons":buttons,"structure":structinfo,"idata":idata,"hwr":hwr,"constellation":constellation,"ship_defs":ship_defs,"starmap":starmap,"messages":msgs}
				self.send_msg(200,json.dumps(msg))
			elif path == "/trade.html":
				if not tstructure:
					raise error.Page()
				tstructure.tick()
				tstructure.make_ships()
				quest_end_text = None
				if command == "transfer":
					self.check(data,"data")
					tstructure.transfer(cdata,data["data"])
					stats.update_ship(pship)
				elif command == "give-credits":
					self.check(data,"amount")
					structure.give_credits(data,cdata,tstructure)
				elif command == "take-credits":
					self.check(data,"amount")
					structure.take_credits(data,cdata,tstructure)
				elif command == "quest-accept":
					self.check(data,"quest-id")
					quest.accept(self,data,cdata)
				elif command == "quest-cancel":
					self.check(data,"quest-id")
					quest.cancel(self,data,cdata)
				elif command == "quest-submit":
					self.check(data,"quest-id")
					quest_end_text = quest.submit(self,data,cdata)
				elif command == "start-build":
					self.check(data,"blueprint")
					build.start(data,cdata,tstructure)
				elif command == "equip-blueprint":
					self.check(data,"blueprint")
					build.equip_blueprint(data,cdata,tstructure,pship)
				elif command == "repair":
					self.check(data,"ship","hull","armor")
					tstructure.repair(self,data,cdata)
				elif command == "update-trade":
					tstructure.update_trade(cdata,data)
				prices = tstructure.get_prices()
				itypes = {}
				for item in prices.keys():
					itype = items.type(item)
					if itype not in itypes:
						itypes[itype] = []
					itypes[itype].append(item)
				quest_defs = quest.get_local(cdata)
				cquests = quest.get_character(cdata)
				idata = items.structure_itemdata(tstructure) | items.character_itemdata(cdata) | items.itemlist_data(prices.keys())
				pships = map.get_character_ships(cdata)
				station_def = defs.ship_types[tstructure["ship"]]
				bp_info = build.get_bp_info(tstructure)
				ship_defs = {}
				for data in pships.values():
					ship_defs[data["type"]] = defs.ship_types[data["type"]]
				industry_defs = tstructure.get_industries()
				next_tick = tstructure.next_tick()
				repair_fees = tstructure.get_repair_fees()
				msgs = self.get_messages()
				msg = {"cdata":cdata,"ship":pship,"ships":pships,"structure":tstructure,"itypes":itypes,"quests":quest_defs,"cquests":cquests,"idata":idata,"prices":prices,"station_def":station_def,"bp_info":bp_info,"ship_defs":ship_defs,"industry_defs":industry_defs,"next_tick":next_tick,"messages":msgs,"repair_fees":repair_fees,"quest_end_text":quest_end_text}
				self.send_msg(200,json.dumps(msg))
			elif path == "/battle.html":
				if command == "attack":
					self.check(data,"rounds")
					pbattle = Battle.attack(cdata)
				elif command == "retreat":
					Battle.retreat(pbattle,self)
				msgs = self.get_messages()
				msg = {"cdata":cdata,"battle":pbattle,"messages":msgs}
				self.send_msg(200,json.dumps(msg))
			elif path == "/quests.html":
				quest_defs = {}
				for q in cdata["quests"].keys():
					quest_defs[q] = defs.quests[q]
				msg = {"cdata":cdata,"quests":quest_defs}
				self.send_msg(200,json.dumps(msg))
			elif path == "/items.html":
				udata = None
				if command == "userdata-update":
					self.check(data,"data")
					io.write2("userdata",cdata["name"],data["data"])
					udata = data["data"]
				if not udata:
					try:
						udata = io.read2("userdata",cdata["name"])
					except Exception as e:
						print(e)
						udata = {}
				msg = {"data":udata}
				self.send_msg(200,json.dumps(msg))
		except error.Auth as e:
			self.redirect(303,"text/html","login.html")
		except error.Char as e:
			self.redirect(303,"text/html","characters.html")
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
				self.redirect(302,"text/html","/main.html")
			else:
				self.response(404,"text/plain")
		elif ftype == ".js":
			self.send_file(200,"text/javascript",file,config["text_cache"])
		elif ftype == ".css":
			self.send_file(200,"text/css",file,config["text_cache"])
		elif ftype == ".png":
			self.send_file(200,"image/png",file,config["image_cache"],True)
		elif ftype == ".webp":
			self.send_file(200,"image/webp",file,config["image_cache"],True)
		elif ftype == ".svg":
			self.send_file(200,"image/svg+xml",file,config["image_cache"],True)
		elif ftype == ".html":
			print(path)
			self.send_file(200,"text/html",file,config["text_cache"])
	def no_log(self,*args):
		#This function is used to stop the server from logging.
		return
	def add_message(self,text):
		if not hasattr(self,"messages"):
			setattr(self,"messages",[])
		self.messages.append(text)
	def get_messages(self):
		if hasattr(self,"messages"):
			return self.messages
		return []
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
	def send_file(self,code,type,path,max_age=None,use_stale=False):
		if max_age:
			self.response(code,type,"Cache-Control",max_age)
			#if use_stale:
			#	self.response(code,type,"stale-while-revalidate",86400)
		else:
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
print("Server has stopped for some reason.")