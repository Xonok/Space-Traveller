import hashlib,random,copy,time,json

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
	real_ip = server.headers.get("X-Real-IP")
	if not real_ip:
		real_ip = server.client_address[0]
	udata["props"]["last_ip"] = real_ip
	udata.save()
from . import defs,io,ship,error,map,types,stats