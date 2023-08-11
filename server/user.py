import hashlib,random,copy

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
def check_pass(username,password):
	return defs.users[username]["key"] == encode(username,password)
def check_key(key):
	if key in defs.session_to_user:
		return defs.session_to_user[key]
	raise error.Auth()
def register(self,username,password):
	if check_user(username): raise error.User("Username already exists.")
	#More conditions here, raise error.User if something is bad.
	new_user = types.make({
		"name": username,
		"key": encode(username,password),
		"session": "",
		"active_character": "",
		"characters": []
	},"user")
	defs.user_names.append(username)
	defs.users[username] = new_user
	io.write2("","users",defs.user_names)
	new_user.save()
	self.send_msg(201,"Success.")
	raise error.Fine()
def make_character(self,data,udata):
	cname = data["name"]
	starter_name = data["starter"]
	if starter_name not in defs.starters: raise error.User("Invalid starter: "+starter_name)
	if cname in defs.characters: raise error.User("A character with that name already exists.")
	if not len(cname): raise error.User("Character name empty.")
	starter = defs.starters[starter_name]
	udata["characters"].append(cname)
	cdata = types.copy(defs.defaults["character"],"character")
	cdata["name"] = cname
	cdata["credits"] = starter["credits"]
	defs.characters[cname] = cdata
	defs.character_ships[cname] = {}
	for ship_data in starter["ships"]:
		for name,items in ship_data.items():
			pship = ship.new(name,cname)
			for item,amount in items["items"].items():
				pship["inventory"]["items"].add(item,amount)
			for item,amount in items["gear"].items():
				pship["inventory"]["gear"].add(item,amount)
			stats.update_ship(pship)
			cdata["ship"] = pship["name"]
			cdata["ships"].append(pship["name"])
			pship["pos"] = copy.deepcopy(starter["pos"])
			system = pship["pos"]["system"]
			x = pship["pos"]["x"]
			y = pship["pos"]["y"]
			map.add_ship(pship,system,x,y)
			ship.add_character_ship(pship)
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
from . import defs,io,ship,error,map,types,stats