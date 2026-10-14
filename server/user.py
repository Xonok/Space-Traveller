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
def update_active(udata,req):
	if "props" not in udata:
		udata["props"] = {}
	udata["props"]["last_active"] = time.time()
	real_ip = req["headers"].get("X-Real-IP")
	#real_ip = client.headers.get("X-Real-IP")
	if not real_ip:
		real_ip = req["client_addr"][0]
	udata["props"]["last_ip"] = real_ip
	udata.save()
from . import defs,io,error
