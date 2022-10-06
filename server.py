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

import http.server,os,ssl,json,hashlib,random
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs

cwd = os.path.dirname(os.path.abspath(__file__))

def write(fname,table):
	with open(fname,"w") as f:
		f.write(json.dumps(table))
def read(fname):
	try:
		with open(fname,"r") as f:
			return json.loads(f.read())
	except:
		return {}

users = read("users.data")
user_key = read("user_keys.data")
key_user = read("key_users.data")
systems = {}
systems["Ska"] = read(os.path.join("map","Ska.json"))
player_data = read("players.data")
markets = {}
markets["Ska"] = read(os.path.join("market","Ska.json"))

def get_file_data(path):
	with open(path,"rb") as f:
		return f.read()
def encode(username,password):
	m = hashlib.sha256((username+password).encode())
	return m.hexdigest()
def make_key(user):
	while True:
		key = str(random.randint(1000000,2000000))
		if key not in key_user:
			if user in user_key.keys():
				del key_user[user_key[user]]
			user_key[user] = key
			key_user[key] = user
			write("user_keys.data",user_key)
			write("key_users.data",key_user)
			return key
def get_tile(system_name,x,y):
	system = systems[system_name]
	x = str(x)
	y = str(y)
	if x not in system or y not in system[x]:
		return {}
	else:
		return system[x][y]
def check_market(system_name,x,y):
	if system_name not in markets:
		return
	market_list = markets[system_name]
	if x not in market_list or y not in market_list[x]:
		if system_name == "Ska" and x == "1" and y == "0":
			if x not in market_list:
				market_list[x] = {}
			market_list[x][y] = {
				"credits": 1000000,
				"items":{
					"energy": {
						"amount": 0,
						"buy": 50,
						"sell": 100
					},
					"gas": {
						"amount": 0,
						"buy": 100,
						"sell": 200
					}
				}
			}
			write(os.path.join("market",system_name+".json"),markets[system_name])
			return True
		else:
			return
	else:
		return True
def get_market(system_name,x,y):
	x = str(x)
	y = str(y)
	if not check_market(system_name,x,y):
		return None
	market_list = markets[system_name]
	return market_list[x][y]
def add_item(inv,name,amount):
	if name not in inv:
		inv[name] = 0
	inv[name] += amount
	if inv[name] == 0:
		del inv[name]
def remove_item(inv,name,amount):
	if name not in inv:
		return 0
	amount = min(inv[name],amount)
	inv[name] -= amount
	if inv[name] == 0:
		del inv[name]
	return amount
def dice(amount,sides):
	sum = 0
	for i in range(amount):
		sum += random.randint(1,sides)
	return sum
def player_check(user):
	if user not in player_data:
		player_data[user] = {
			"position":(1,0),
			"system":"Ska",
			"credits":10000,
			"items":{},
			"space_available":50,
			"space_total":50,
			"img":"img/clipart2908532.png",
			"rotation":0
		}
def do_trade(pdata,data,market):
	player_items = pdata["items"]
	player_credits = pdata["credits"]
	buy = data["buy"]
	sell = data["sell"]
	market_items = market["items"]
	market_credits = market["credits"]
	success = False
	for item,amount in sell.items():
		price = market_items[item]["buy"]
		stock = player_items[item]
		#Can't sell less than 0.
		amount = max(amount,0)
		#Can't sell more than you have, or more than market has money for.
		amount = min(amount,stock,market_credits//price)
		if amount == 0:
			#Don't bother updating anything.
			continue
		player_items[item] -= amount
		if not player_items[item]:
			del player_items[item]
		player_credits += amount*price
		market_items[item]["amount"] += amount
		market_credits -= amount*price
		pdata["space_available"] += amount
		success = True
	for item,amount in buy.items():
		price = market_items[item]["sell"]
		stock = market_items[item]["amount"]
		#Can't buy less than 0.
		amount = max(amount,0)
		#Can't buy more than market has, or more than the player has money for.
		amount = min(amount,stock,player_credits//price)
		if amount == 0:
			#Don't bother updating anything.
			continue
		player_items[item] += amount
		if not player_items[item]:
			del player_items[item]
		player_credits -= amount*price
		market_items[item]["amount"] -= amount
		market_credits += amount*price
		pdata["space_available"] -= amount
		success = True
	if success:
		pdata["items"] = player_items
		pdata["credits"] = player_credits
		market["items"] = market_items
		market["credits"] = market_credits
		write("players.data",player_data)
		system_name = pdata["system"]
		write(os.path.join("market",system_name+".json"),markets[system_name])

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
				print("register")
				if username in users:
					self.send_msg(401,"Username already exists.")
					return
				users[username] = encode(username,password)
				write("users.data",users)
				self.send_msg(201,"Success.")
			elif command == "login":
				if username not in users:
					self.send_msg(401,"Username doesn't exist.")
					return
				digest = encode(username,password)
				if users[username] != digest:
					self.send_msg(401,"Invalid password.")
					return
				key = make_key(username)
				self.redirect(302,"text/html","nav.html?key="+str(key))
		elif path == "/nav.html":
			if not self.check(data,"command","key"):
				return
			command = data["command"]
			key = data["key"]
			if key in key_user:
				user = key_user[key]
			else:
				self.redirect(401,"text/html","login.html")
				return
			player_check(user)
			pdata = player_data[user]
			system = pdata["system"]
			px,py = pdata["position"]
			if command == "move":
				if not self.check(data,"position"):
					return
				prev_x,prev_y = px,py
				px,py = data["position"]
				tile = get_tile(system,px,py)
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
				tile = get_tile(system,px,py)
				if "color" in tile:
					if tile["color"] == "#000000":
						print("a")
					elif tile["color"] == "#00bfff":
						res = dice(2,6)
						res = min(pdata["space_available"],res)
						pdata["space_available"] -= res
						add_item(pdata["items"],"energy",res)
					elif tile["color"] == "#ff0000":
						res = dice(3,6)
						res = min(pdata["space_available"],res)
						pdata["space_available"] -= res
						add_item(pdata["items"],"gas",res)
			elif command == "drop":
				if not self.check(data,"items"):
					return
				items = data["items"]
				for name,amount in items.items():
					pdata["space_available"] += remove_item(pdata["items"],name,amount)
			elif command == "dock":
				self.redirect(303,"text/html","trade.html")
				return
			write("players.data",player_data)
			tiles = {}
			vision = 5
			for x in range(px-vision,px+vision+1):
				if x not in tiles:
					tiles[x] = {}
				for y in range(py-vision,py+vision+1):
					tiles[x][y] = get_tile(system,x,y)
			buttons = {
				"gather":"initial",
				"drop_all":"none",
				"dock":"none"
			}
			if pdata["space_available"] != pdata["space_total"]:
				buttons["drop_all"] = "initial"
			market = get_market(system,px,py)
			if market:
				buttons["dock"] = "initial"
			msg = {"tiles":tiles,"pdata":pdata,"buttons":buttons}
			self.send_msg(200,json.dumps(msg))
		elif path == "/trade.html":
			if not self.check(data,"command","key"):
				return
			command = data["command"]
			key = data["key"]
			if key in key_user:
				user = key_user[key]
			else:
				self.redirect(401,"text/html","login.html")
				return
			player_check(user)
			pdata = player_data[user]
			system = pdata["system"]
			px,py = pdata["position"]
			market = get_market(system,px,py)
			if not market:
				self.redirect(303,"text/html","nav.html")
				return
			if command == "trade-goods":
				if not self.check(data,"buy","sell"):
					return
				do_trade(pdata,data,market)
			msg = {"pdata":pdata,"market":market}
			self.send_msg(200,json.dumps(msg))
	def do_GET(self):
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
		self.wfile.write(get_file_data(path))
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
