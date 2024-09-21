import hashlib,random,copy,time

class User(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
	def save(self):
		io.write2("users",self["name"],self)

def encode(username,password):
	m = hashlib.sha256((username+password).encode())
	return m.hexdigest()
def make_key(user_name):
	user = defs.users[user_name]
	while True:
		session = str(random.randint(1000000,2000000))
		if session not in defs.session_to_user:
			prev_key = user["session"]
			if prev_key in defs.session_to_user:
				del defs.session_to_user[prev_key]
			user["session"] = session
			defs.session_to_user[session] = user_name
			user.save()
			return session
def check_user(username):
	return username in defs.users
def check_user_deep(username):
	return username.lower() in defs.users_lowercase
def check_character_deep(cname):
	return cname.lower() in defs.characters_lowercase
def check_pass(username,password):
	return defs.users[username]["key"] == encode(username,password)
def check_key(key):
	if key in defs.session_to_user:
		return defs.session_to_user[key]
	raise error.Auth()
def name_valid(name):
	alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	connector = " -_'"
	min_length = 3
	max_length = 20
	if len(name) < min_length or len(name) > max_length:
		raise error.User("Names must be at least 3 and no more than 20 characters long.")
	for k in connector:
		if name.startswith(k) or name.endswith(k):
			raise error.User("Can't start or end a name with any of the following: \""+connector+"\"")
	for k in name:
		if k not in alphabet and k not in connector:
			raise error.User("The only characters allowed in names are ascii characters, spacebar( ), hyphen(-) and underscore(_).")
def register(self,username,password):
	if check_user_deep(username): raise error.User("User with that name already exists.")
	name_valid(username)
	#More conditions here, raise error.User if something is bad.
	new_user = types.make({
		"name": username,
		"key": encode(username,password),
		"session": "",
		"active_character": "",
		"characters": [],
		"props": {
			"created": time.time()
		}
	},"user")
	defs.user_names.append(username)
	defs.users[username] = new_user
	defs.users_lowercase[username.lower()] = new_user
	io.write2("","users",defs.user_names)
	new_user.save()
	self.send_msg(201,"Success.")
	raise error.Fine()
def make_character(self,data,udata):
	cname = data["name"]
	if check_character_deep(cname): raise error.User("Character with that name already exists.")
	starter_name = data["starter"]
	if starter_name not in defs.starters: raise error.User("Invalid starter: "+starter_name)
	if not len(cname): raise error.User("Character name empty.")
	name_valid(cname)
	starter = defs.starters[starter_name]
	udata["characters"].append(cname)
	cdata = types.copy(defs.defaults["character"],"character")
	cdata["name"] = cname
	cdata["credits"] = starter["credits"]
	cdata["home"] = starter["home"]
	cdata["props"] = {}
	cdata["props"]["time_created"] = time.time()
	defs.characters[cname] = cdata
	defs.characters_lowercase[cname.lower()] = cdata
	defs.character_ships[cname] = {}
	for entry in starter["ships"]:
		for name,ship_data in entry.items():
			pship = ship.new(name,cname)
			for item,amount in ship_data["gear"].items():
				pship["gear"].add(item,amount)
			pship.init()
			stats.update_ship(pship)
			cdata["ship"] = pship["name"]
			cdata["ships"].append(pship["name"])
			pship["pos"] = copy.deepcopy(starter["pos"])
			system = pship["pos"]["system"]
			x = pship["pos"]["x"]
			y = pship["pos"]["y"]
			map.add_ship(pship,system,x,y)
			ship.add_character_ship(pship)
	cdata.init()
	udata.save()
	cdata.save()
def select_character(self,data,udata):
	if data["character"] not in udata["characters"]:
		raise error.User("You don't have a character with that name.")
	udata["active_character"] = data["character"]
	udata.save()
	raise error.Page()
def handle_login(self,data):
	self.check(data,"command","username","password")
	command = data["command"]
	username = data["username"]
	password = data["password"]
	if command == "register":
		register(self,username,password)
	elif command == "login":
		if not check_user(username):
			raise error.User("Username doesn't exist.")
		elif not check_pass(username,password):
			raise error.User("Invalid password.")
		else:
			self.send_msg(200,str(make_key(username)))
			raise error.Fine()
def update_active(udata,server):
	if "props" not in udata:
		udata["props"] = {}
	udata["props"]["last_active"] = time.time()
	udata["props"]["last_ip"] = server.client_address[0]
	udata.save()
from . import defs,io,ship,error,map,types,stats