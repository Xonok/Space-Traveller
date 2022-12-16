import http.server,os,ssl,json,copy
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from server import io,user,player,func,items,factory,ship,defs,structure,map,quest,error

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
			pdata = defs.players.get(username)
			pship = ship.get(pdata.ship())
			pitems = pship.get_items()
			psystem = pship.get_system()
			stiles = map.get_system(psystem)["tiles"]
			px,py = pship.get_coords()
			tstructure = structure.get(psystem,px,py)
			if path == "/nav.html":
				if command == "move":
					map.move(self,data,pdata)
				elif command == "gather":
					map.gather(stiles,px,py,pdata)
				elif command == "drop":
					items.drop(self,data,pitems)
				elif command == "use_item":
					items.use(self,data,pdata)
				px,py = pship.get_coords()
				tstructure = structure.get(psystem,px,py)
				structinfo = {}
				if tstructure:
					structinfo = {
						"name": tstructure["name"],
						"type": tstructure["type"],
						"image": defs.ship_types[tstructure["ship"]]["img"]
					}
				pship.get_space()
				pship.save()
				vision = 5
				tiles = map.get_tiles(psystem,px,py,vision)
				tile = map.get_tile(psystem,px,py,username)
				buttons = {
					"gather": "initial",
					"drop_all": "initial" if len(pitems) else "none",
				}
				idata = items.player_itemdata(pdata)
				msg = {"tiles":tiles,"tile":tile,"pdata":pdata,"ship":pship,"buttons":buttons,"structure":structinfo,"idata":idata}
				self.send_msg(200,json.dumps(msg))
			elif path == "/trade.html":
				if not tstructure:
					raise error.Page()
				tstructure.tick()
				if command == "trade-goods":
					self.check(data,"buy","sell")
					tstructure.trade(pdata,data)
				elif command == "transfer-goods":
					self.check(data,"take","give","take_gear","give_gear")
					tstructure.transfer(pdata,data)
				elif command == "equip":
					self.check(data,"ship-on","ship-off","station-on","station-off")
					tstructure.equip(data)
					pdata.equip(data)
				elif command == "quest-accept":
					self.check(data,"quest-id")
					quest.accept(self,data,pdata)
				elif command == "quest-cancel":
					self.check(data,"quest-id")
					quest.cancel(self,data,pdata)
				elif command == "quest-submit":
					self.check(data,"quest-id")
					quest.submit(self,data,pdata)
				elif command == "ship-buy":
					self.check(data,"ship")
					tstructure.buy_ship(data,pdata)
				elif command == "ship-enter":
					self.check(data,"ship")
					ship.enter(data,pdata)
					pship = ship.get(pdata.ship())
				tstructure.item_change()
				itypes = {}
				for item in tstructure["market"]["prices"].keys():
					itype = items.type(item)
					if itype not in itypes:
						itypes[itype] = []
					itypes[itype].append(item)
				quests = tstructure["quests"]
				quest_defs = {}
				for q in quests:
					quest_defs[q] = defs.quests[q]
				idata = items.structure_itemdata(tstructure,pdata) | items.player_itemdata(pdata)
				pships = map.get_player_ships(pdata)
				msg = {"pdata":pdata,"ship":pship,"ships": pships,"structure":tstructure,"itypes":itypes,"quests":quest_defs,"idata":idata}
				self.send_msg(200,json.dumps(msg))
		except error.Auth as e:
			self.redirect(303,"text/html","login.html")
		except error.Page as e:
			self.redirect(303,"text/html","nav.html")
		except error.User as e:
			self.send_msg(400,str(e))
		except error.Fine as e:
			return
		except Exception as e:
			self.send_msg(500,"Server error")
			raise
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
				raise error.User("Missing required \""+arg+"\"")

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(".ssh/certificate.pem",".ssh/key.pem")
httpd = http.server.HTTPServer(("", 443), MyHandler)
httpd.socket = context.wrap_socket(httpd.socket,server_side=True)
httpd.serve_forever()
