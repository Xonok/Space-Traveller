import time,copy,hashlib,random

from . import api
from server import user,error,defs,types,ship,stats,map,io

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
def register(ctx,username="str",password="str"):
	server = ctx["server"]
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
	server.send_msg(201,"Success.")
	raise error.Fine()
def login(ctx,username="str",password="str"):
	server = ctx["server"]
	if not check_user(username):
		raise error.User("Username doesn't exist.")
	elif not check_pass(username,password):
		raise error.User("Invalid password.")
	else:
		server.send_msg(200,str(make_key(username)))
		raise error.Fine()
def make_character(ctx,cname="str",starter="str"):
	udata = ctx["udata"]
	if check_character_deep(cname): raise error.User("Character with that name already exists.")
	if starter not in defs.starters: raise error.User("Invalid starter: "+starter)
	if not len(cname): raise error.User("Character name empty.")
	name_valid(cname)
	starter_def = defs.starters[starter]
	udata["characters"].append(cname)
	cdata = types.copy(defs.defaults["character"],"character")
	cdata["name"] = cname
	cdata["credits"] = starter_def["credits"]
	cdata["home"] = starter_def["home"]
	cdata["props"] = {}
	cdata["props"]["time_created"] = time.time()
	defs.characters[cname] = cdata
	defs.characters_lowercase[cname.lower()] = cdata
	defs.character_ships[cname] = {}
	for entry in starter_def["ships"]:
		for name,ship_data in entry.items():
			pship = ship.new(name,cname)
			for item,amount in ship_data["gear"].items():
				pship["gear"].add(item,amount)
			pship.init()
			stats.update_ship(pship)
			cdata["ship"] = pship["name"]
			cdata["ships"].append(pship["name"])
			pship["pos"] = copy.deepcopy(starter_def["pos"])
			system = pship["pos"]["system"]
			x = pship["pos"]["x"]
			y = pship["pos"]["y"]
			map.add_ship(pship,system,x,y)
			ship.add_character_ship(pship)
	cdata.init()
	udata.save()
	cdata.save()
def select_character(ctx,character="str"):
	udata = ctx["udata"]
	if character not in udata["characters"]:
		raise error.User("You don't have a character with that name.")
	udata["active_character"] = character
	udata.save()
	raise error.Page()
api.register("register",register,auth=False)
api.register("login",login,auth=False)
api.register("make-character",make_character)
api.register("select-character",select_character)