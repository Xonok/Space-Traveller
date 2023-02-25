import hashlib,random,copy

class User(dict):
	def __init__(self,**kwargs):
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
	defs.users[username] = encode(username,password)
	cdata = copy.deepcopy(defs.defaults["character"])
	cdata["name"] = username
	pship = ship.new("harvester",username)
	cdata["ship"] = pship["name"]
	cdata["ships"] = [pship["name"]]
	defs.characters[username] = cdata
	defs.character_ships[username] = {}
	system = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	map.add_ship(pship,system,x,y)
	ship.add_character_ship(pship)
	io.write2("","users",defs.users)
	io.write2("characters",username,cdata)
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
from . import defs,io,ship,error,map