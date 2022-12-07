import http.server,os,ssl,json,copy
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from server import io,user,player,func,items,factory,ship,defs,structure,map,quest

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
		if not username:
			self.redirect(303,"text/html","login.html")
			return
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
			buttons = {
				"gather": "initial",
				"drop_all": "initial" if len(pitems) else "none",
			}
			idata = items.player_itemdata(pdata)
			msg = {"tiles":tiles,"pdata":pdata,"ship":pship,"buttons":buttons,"structure":structinfo,"idata":idata}
			self.send_msg(200,json.dumps(msg))
		elif path == "/trade.html":
			if not tstructure:
				self.redirect(303,"text/html","nav.html")
				return
			tstructure.tick()
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
			elif command == "quest-accept":
				if not self.check(data,"quest-id"):
					return
				quest.accept(self,data,pdata)
			elif command == "quest-cancel":
				if not self.check(data,"quest-id"):
					return
				quest.cancel(self,data,pdata)
			elif command == "quest-submit":
				if not self.check(data,"quest-id"):
					return
				quest.submit(self,data,pdata)
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
			msg = {"pdata":pdata,"ship":pship,"structure":tstructure,"itypes":itypes,"quests":quest_defs,"idata":idata}
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
