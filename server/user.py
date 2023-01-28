import hashlib,random,copy
from . import io,ship,error,map

def encode(username,password):
	m = hashlib.sha256((username+password).encode())
	return m.hexdigest()
def make_key(user):
	while True:
		key = str(random.randint(1000000,2000000))
		if key not in defs.key_users:
			if user in defs.user_keys.keys():
				del defs.key_users[defs.user_keys[user]]
			defs.user_keys[user] = key
			defs.key_users[key] = user
			io.write2("","user_keys",defs.user_keys)
			return key
def check_user(username):
	return username in defs.users
def check_pass(username,password):
	return defs.users[username] == encode(username,password)
def check_key(key):
	if key in defs.key_users:
		return defs.key_users[key]
	raise error.Auth()
def register(self,username,password):
	if check_user(username): raise error.User("Username already exists.")
	#More conditions here, raise error.User if something is bad.
	defs.users[username] = encode(username,password)
	pdata = copy.deepcopy(defs.defaults["player"])
	pdata["name"] = username
	pship = ship.new("harvester",username)
	pdata["ship"] = pship["name"]
	pdata["ships"] = [pship["name"]]
	defs.players[username] = pdata
	defs.player_ships[username] = {}
	system = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	map.add_ship(pship,system,x,y)
	ship.add_player_ship(pship)
	io.write2("","users",defs.users)
	io.write2("players",username,pdata)
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
from . import defs
