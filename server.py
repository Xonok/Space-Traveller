#CODE STATUS - too many responsibilities
#*This file should only set up the server and let other files handle the rest.
#*Commands in particular should not depend on page and should be moved to the new system.
#*Sometimes the lives server stops responding. The reason has something to do with http.server
#Maybe we should write our own simplified implementation?

import http.server,os,ssl,json,gzip,_thread,traceback,time,math
import dumb_http
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from server import io,user,items,ship,defs,structure,map,quest,error,chat,hive,loot,gathering,build,archeology,spawner,stats,Battle,config,Command,lore,character,Item,art,Skill,Character,exploration,reputation,wiki,html,cache,Query,Analysis

new_server = True

baseclass = dumb_http.DumbHandler if new_server else BaseHTTPRequestHandler
class MyHandler(baseclass):
	def __init__(self,*args):
		if not config.config["logging"]:
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
			command = data["command"]
			username = user.check_key(data["key"])
			response = Command.process(self,data)
			now = time.time()
			if path == "/chat.html":
				chat.handle_command(self,data,username)
				raise error.User("Unknown command for chat page: "+command)
			udata = defs.users.get(username)
			if "char" in data and data["char"] in udata["characters"]:
				udata["active_character"] = data["char"]
			user.update_active(udata,self)
			cdata = defs.characters.get(udata["active_character"])
			if not cdata and path != "/characters.html":
				print("No cdata")
				raise error.Char()
			msg = {}
			if cdata:
				character.update_active(cdata)
				cname = cdata["name"]
				if "ship" in data:
					if ship.get(data["ship"])["owner"] != cname: raise error.User("You don't own that ship.")
					cdata["ship"] = data["ship"]
				pship = ship.get(cdata.ship())
				for ps in ship.gets(cdata["name"]).values():
					ps.tick()
				psystem = pship.get_system()
				px,py = pship.get_coords()
				tstructure = structure.get(psystem,px,py)
				pbattle = Battle.get(cdata)
				if pbattle and path == "/nav.html" and path == "/dock.html":
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
				active_ships = {}
				for c in pchars:
					cdata = defs.characters.get(c)
					pship = ship.get(cdata["ship"])
					active_ships[c] = pship["img"]
				msg = {"characters":pchars,"active_character":udata["active_character"],"starters":defs.starters,"active_ships":active_ships}
			elif path == "/nav.html":
				if command == "excavate":
					archeology.excavate(self,cdata,tstructure)
				elif command == "investigate":
					archeology.investigate(self,cdata,tstructure)
				elif command == "drop":
					items.drop(self,data,cdata,pship)
				elif command == "use_item":
					items.use(self,data,cdata)
				elif command == "ship-trade":
					self.check(data,"data")
					pship.trade(cdata,data["data"])
				elif command == "give-credits-character":
					self.check(data,"target","amount")
					character.give_credits(cdata,data)
				elif command == "jump":
					map.jump(self,cdata)
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
					hive.use_homeworld_return(cdata)
				elif command == "take-loot":
					self.check(data,"items")
					loot.take(data,cdata)
				elif command == "pack-station":
					structure.pick_up(pship,cdata)
				elif command == "ship-rename":
					self.check(data,"name")
					pship.rename(data["name"])
				spawner.tick()
				px,py = pship.get_coords()
				psystem = pship.get_system()
				gathering.update_resources(psystem,px,py)
				tstructure = structure.get(psystem,px,py)
				if tstructure:
					exploration.check_visit(cdata,tstructure["name"],self)
				structinfo = {}
				if tstructure:
					structinfo = {
						"name": tstructure["name"],
						"custom_name": tstructure.get("custom_name"),
						"type": tstructure["type"],
						"ship": defs.ship_types[tstructure["ship"]]["name"],
						"owner": tstructure["owner"],
						"img": defs.ship_types[tstructure["ship"]]["img"],
						"structure": True
					}
				pship.get_room()
				Character.update_command_slots(cdata)
				pship.save()
				cdata.save()
				pships = map.get_character_ships(cdata)
				vision = 3
				tile = map.get_tile(psystem,px,py)
				ship_defs = {}
				for data in pships.values():
					ship_defs[data["type"]] = defs.ship_types[data["type"]]
					pgear = data.get_gear()
					if "highpower_scanner" in pgear:
						vision = max(vision,5)
				vision += defs.terrain[tile["terrain"]]["vision"]
				cdata["stats"]["vision"] = vision
				# tiles = map.get_tiles(psystem,px,py,vision)
				buttons = {
					"gather": "initial" if tile["resource"] else "none",
					"excavate": "initial" if archeology.can_excavate(cdata,tstructure) else "none",
					"investigate": "initial" if archeology.can_investigate(cdata,tstructure) else "none",
					"pack": "initial" if tstructure and tstructure["owner"] == cdata["name"] else "none"
				}
				hwr = hive.hwr_info(cdata)
				constellation = defs.constellation_of.get(pship["pos"]["system"])
				if not constellation:
					constellation = "Unknown"
				idata = items.character_itemdata(cdata)
				starmap = map.get_star_data_small(pship["pos"]["system"])
				characters = Character.query.get_tile_characters(tile)
				msgs = self.get_messages()
				msg = {"vision":vision,"tile":tile,"cdata":cdata,"ships":pships,"buttons":buttons,"structure":structinfo,"idata":idata,"hwr":hwr,"constellation":constellation,"ship_defs":ship_defs,"starmap":starmap,"characters":characters,"messages":msgs}
			elif path == "/dock.html":
				if not tstructure:
					raise error.Page()
				tstructure.tick()
				tstructure.make_ships()
				quest_end_text = None
				if command == "transfer":
					self.check(data,"data")
					tstructure.transfer(cdata,data["data"],self)
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
					build.equip_blueprint(data,cdata,tstructure)
				elif command == "unequip-blueprint":
					self.check(data,"blueprint")
					build.unequip_blueprint(data,cdata,tstructure)
				elif command == "repair":
					self.check(data,"ship","hull","armor")
					tstructure.repair(self,data,cdata)
				elif command == "repair-all":
					tstructure.repair_all(self,cdata)
				elif command == "update-trade":
					tstructure.update_trade(cdata,data)
				elif command == "update-name":
					self.check(data,"structure","name")
					structure.update_name(data,cdata)
				elif command == "update-desc":
					self.check(data,"structure","desc")
					structure.update_desc(data,cdata)
				elif command == "structure-next-tick":
					tstructure.force_next_tick(udata)
				elif command == "structure-update-limits":
					self.check(data,"limits")
					tstructure.update_limits(data,cdata)
				elif command == "update-transport":
					self.check(data,"entries","next_action")
					Item.transport.update_actions(tstructure,data["entries"],data["next_action"])
				elif command == "skill-train":
					self.check(data,"name")
					Skill.train_skill(cdata,data["name"],tstructure)
				elif command == "set-home":
					tstructure.set_home(cdata)
				elif command == "planet-donate-credits":
					self.check(data,"amount","target")
					tstructure.donate_credits(self,cdata,data)
				elif command == "ship-pack":
					self.check(data,"target")
					tstructure.pack_ship(self,cdata,data)
				prices = tstructure.get_prices()
				itypes = {}
				for item in prices.keys():
					itype = items.type(item)
					if itype not in itypes:
						itypes[itype] = []
					itypes[itype].append(item)
				tile = map.get_tile(psystem,px,py)
				quest_defs = quest.get_local(cdata)
				cquests = quest.get_character(cdata)
				idata = items.structure_itemdata(tstructure) | items.character_itemdata(cdata) | items.itemlist_data(prices.keys())
				pships = map.get_character_ships(cdata)
				bp_info = build.get_bp_info(tstructure)
				ind_defs = tstructure.get_industries()
				ship_defs = {}
				for data in pships.values():
					ship_defs[data["type"]] = defs.ship_types[data["type"]]
				ship_defs[tstructure["ship"]] = defs.ship_types[tstructure["ship"]]
				next_tick = tstructure.next_tick()
				repair_fees = tstructure.get_repair_fees()
				transport_targets = map.get_owned_structures(pship["pos"]["system"],cdata["name"])
				msgs = self.get_messages()
				msg = {"cdata":cdata,"ship":pship,"ships":pships,"structure":tstructure,"itypes":itypes,"quests":quest_defs,"cquests":cquests,"idata":idata,"prices":prices,"bp_info":bp_info,"ship_defs":ship_defs,"next_tick":next_tick,"messages":msgs,"repair_fees":repair_fees,"quest_end_text":quest_end_text,"industry_defs":ind_defs,"transport_targets":transport_targets,"tile":tile}
				if tstructure:
					skill_loc = Skill.get_location(tstructure["name"])
					if skill_loc:
						msg["skill_loc"] = skill_loc
						msg["skill_data"] = Skill.get_skill_data(skill_loc)
			elif path == "/battle.html":
				if command == "attack":
					self.check(data,"rounds")
					pbattle = Battle.attack(cdata)
				elif command == "retreat":
					temp = Battle.retreat(pbattle,self)
					if temp:
						pbattle = temp
				pships = map.get_character_ships(cdata)
				ship_defs = {}
				for data in pships.values():
					ship_defs[data["type"]] = defs.ship_types[data["type"]]
				if pbattle:
					for side in pbattle["sides"]:
						for name,data in side["combat_ships"].items():
							ship_defs[data["ship"]["type"]] = defs.ship_types[data["ship"]["type"]]
				msgs = self.get_messages()
				msg = {"cdata":cdata,"battle":pbattle,"ship_defs":ship_defs,"messages":msgs}
			elif path == "/quests.html":
				quest_defs = {}
				for q in cdata["quests"].keys():
					quest_defs[q] = defs.quests[q]
				msg = {"cdata":cdata,"quests":quest_defs}
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
			elif path == "/lore.html":
				msg = {"lore_entries":lore.entries()}
				if command == "request-lore":
					self.check(data,"name")
					msg["request_name"] = data["name"]
					msg["request_data"] = lore.request(data["name"])
			elif path == "/map.html":
				msg = {}
				if command == "get-map-data":
					self.check(data,"star")
					msg["star_data"] = map.get_star_data(data)
			elif path == "/art.html":
				msg = {}
				msg["images"] = art.get_all_images()
			elif path == "/profile.html":
				msg = {}
				msg["achievements"] = exploration.get_achievements(cdata)
				msg["cdata"] = cdata
				msg["net_worth"] = Item.query.net_worth(cdata)
				msg["pships"] = ship.character_ships(cdata["name"])
				msg["structures"] = structure.character_structures(cdata["name"])
				msg["reputation"] = reputation.get_total(cdata["name"])
				msg["skills"] = Skill.get_character_skills(cdata)
			elif path == "/user.html":
				msg = {}
				self.send_msg(200,json.dumps(msg))
			elif path == "/wiki.html":
				msg = {}
				if command == "get-wiki-page":
					self.check(data,"page")
					wiki.get_page(data,msg,cdata)
			msg = msg | response
			Query.process_command(command,msg,cdata)
			self.send_msg(200,json.dumps(msg))
			later = time.time()
			d_t = later-now
			# performance.
			print(command+":"+str(math.floor(d_t*1000))+"ms")
		except error.Auth:
			self.redirect(303,"text/html","login.html")
		except error.Char:
			self.redirect(303,"text/html","characters.html")
		except error.Page:
			self.redirect(303,"text/html","nav.html")
		except error.Battle:
			self.redirect(303,"text/html","battle.html")
		except error.User as e:
			self.send_msg(400,str(e))
		except error.Fine:
			return
		except Exception:
			io.clear_writes()
			self.send_msg(500,"Server error")
			print(traceback.format_exc())
	def do_GET(self):
		now = time.time()
		self.protocol_version = "HTTP/1.1"
		url_parts = urlparse(self.path)
		path = url_parts.path
		if path.startswith('/'):
			path = path[1:]
		if path == "chat_async":
			# chat.get(self)
			chat.do_GET(self)
			return
		_,ftype = os.path.splitext(path)
		ftypes = {
			".js": "",
			".css": "",
			".png": "",
			".webp": "",
			".jpg": "",
			".svg": "",
			".html": "html"
		}
		folder = ftypes.get(ftype)
		if folder:
			file = os.path.join(io.cwd,folder,*path.split('/'))
		else:
			file = os.path.join(io.cwd,*path.split('/'))
		if path == '' or (not os.path.exists(file) and file not in cache.cache):
			if ftype == ".html" or ftype == '' or path == '':
				self.redirect(302,"text/html; charset=utf-8","/main.html")
			else:
				self.response(404,"text/plain")
		elif ftype == ".js":
			self.send_file(200,"text/javascript; charset=utf-8",file,True)
		elif ftype == ".css":
			self.send_file(200,"text/css; charset=utf-8",file,True)
		elif ftype == ".png":
			self.send_file(200,"image/png",file)
		elif ftype == ".webp":
			self.send_file(200,"image/webp",file)
		elif ftype == ".jpg":
			self.send_file(200,"image/jpeg",file)
		elif ftype == ".svg":
			self.send_file(200,"image/svg+xml",file,True)
		elif ftype == ".html":
			print(path)
			self.send_html(200,file)
			# self.send_file(200,"text/html",file,config.config["text_cache"])
		later = time.time()
		d_t = later-now
		# print("GET",path,str(math.floor(d_t*1000))+"ms")
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
	def response(self,code,type,opt_type=None,opt_data=None,encoding=None):
		self.send_response(code)
		self.send_header("Content-Type",type)
		if encoding:
			self.send_header("Content-Encoding",encoding)
		self.send_header("Access-Control-Allow-Origin","*")
		if opt_type and opt_data:
			self.send_header(opt_type,opt_data)
		self.end_headers()
	def send_msg(self,code,msg):
		self.response(code,"text/plain",encoding="gzip")
		data = bytes(msg,"utf-8")
		data2 = gzip.compress(data)
		self.wfile.write(data2)
	def send_json(self,msg):
		self.send_msg(200,json.dumps(msg))
	def send_file(self,code,type,path,compress=False):
		if path in cache.cache:
			data = cache.cache[path]
		else:
			data = io.get_file_data(path)
			if config.config["cache"]:
				cache.cache[path] = data
		if compress:
			data2 = gzip.compress(data)
			self.response(code,type,encoding="gzip")
			self.wfile.write(data2)
		else:
			self.response(code,type)
			self.wfile.write(data)
	def send_html(self,code,path):
		data = html.load(path)
		data2 = gzip.compress(data)
		encoding = "gzip"
		len_a = len(data)
		len_b = len(data2)
		type = "text/html; charset=utf-8"
		self.response(code,type,encoding=encoding)
		self.wfile.write(data2)
	def redirect(self,code,type,target):
		self.response(code,type,"Location",target)
	def check(self,msg,*args):
		for arg in args:
			if not arg in msg:
				raise error.User("Missing required \""+arg+"\"")
class HTTP_to_HTTPS(MyHandler):
	def do_POST(self):
		url_parts = urlparse(self.path)
		path = url_parts.path
		self.redirect(301,"text/html","https://"+self.headers["Host"]+path)
	def do_GET(self):
		url_parts = urlparse(self.path)
		path = url_parts.path
		self.redirect(301,"text/html","https://"+self.headers["Host"]+path)
server_type = dumb_http.DumbHTTP if new_server else http.server.ThreadingHTTPServer

# context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# context.load_cert_chain(".ssh/certificate.pem",".ssh/key.pem")
# httpd = server_type(("", 443), MyHandler)
# httpd.socket = context.wrap_socket(httpd.socket,server_side=True)

# httpd2 = server_type(("", 80), HTTP_to_HTTPS)

def run(httpd):
	httpd.serve_forever()
	print("Server has stopped for some reason.")
print("Acquiring ports...")
httpd = None
httpd2 = None
if config.config["backend"]:
	httpd = server_type(("",8200),MyHandler)
	_thread.start_new_thread(run,(httpd,))
else:
	if config.config["ssl"]:
		context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
		context.load_cert_chain(".ssh/certificate.pem",".ssh/key.pem")
		httpd = server_type(("", 443), MyHandler)
		httpd.socket = context.wrap_socket(httpd.socket,server_side=True)

		httpd2 = server_type(("", 80), HTTP_to_HTTPS)
		_thread.start_new_thread(run,(httpd,))
		_thread.start_new_thread(run,(httpd2,))
	else:
		httpd = server_type(("", 80), MyHandler)
		_thread.start_new_thread(run,(httpd,))

MAX_TIMEOUT = 5 #seconds
start_time = time.time()
while True:
	if time.time()-start_time > MAX_TIMEOUT:
		print("Failed to acquire ports.")
		break
	if (httpd is None or httpd.startup_success) and (httpd2 is None or httpd2.startup_success):
	# if httpd3.startup_success:
	# if httpd.startup_success and httpd2.startup_success and httpd3.startup_success:
		print("Ports successfully acquired.")
		io.init()
		break
	time.sleep(0.1)