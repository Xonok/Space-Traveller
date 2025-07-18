import time,copy,hashlib,random

from . import api
from server import user,error,defs,types,ship,stats,map,io,exploration

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
def register(server,username="str",password="str"):
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
	server.send_msg(201,"Account created. Try logging in.")
	raise error.Fine()
def login(server,username="str",password="str"):
	if not check_user(username):
		raise error.User("There is no account with that name.")
	elif not check_pass(username,password):
		raise error.User("Invalid password.")
	else:
		server.send_msg(200,str(make_key(username)))
		raise error.Fine()
def get_characters(udata):
	#This doesn't need to do anything except specify the needed args.
	#Specifically, since cdata is not mentioned, this avoids an error.
	#(cdata comes from auth, which is assumed necessary)
	pass
def make_character(udata,new_cname="str",starter="str"):
	if check_character_deep(new_cname): raise error.User("Character with that name already exists.")
	if starter not in defs.starters: raise error.User("Invalid starter: "+starter)
	if not len(new_cname): raise error.User("Character name empty.")
	name_valid(new_cname)
	starter_def = defs.starters[starter]
	udata["characters"].append(new_cname)
	cdata = types.copy(defs.defaults["character"],"character")
	cdata["name"] = new_cname
	cdata["credits"] = starter_def["credits"]
	cdata["home"] = starter_def["home"]
	cdata["props"] = {}
	cdata["props"]["time_created"] = time.time()
	defs.characters[new_cname] = cdata
	defs.characters_lowercase[new_cname.lower()] = cdata
	defs.character_ships[new_cname] = {}
	for entry in starter_def["ships"]:
		for name,ship_data in entry.items():
			pship = ship.new(name,new_cname)
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
	exploration.check_character(cdata)
	cdata.init()
	udata.save()
	cdata.save()
def select_character(udata,character="str"):
	if character not in udata["characters"]:
		raise error.User("You don't have a character with that name.")
	udata["active_character"] = character
	udata.save()
	raise error.Page()
api.register("register",register)
api.register("login",login)
api.register("get-characters",get_characters,"characters","active-character","starters")
api.register("make-character",make_character,"characters")
api.register("select-character",select_character)
