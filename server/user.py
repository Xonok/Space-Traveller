import hashlib,random,copy
from . import io

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
			io.write2("","key_users",defs.key_users)
			return key
def check_user(username):
	return username in defs.users
def check_pass(username,password):
	return defs.users[username] == encode(username,password)
def check_key(key):
	if key in defs.key_users:
		return defs.key_users[key]
def register(username,password):
	if check_user(username):
		return False
	defs.users[username] = encode(username,password)
	pdata = copy.deepcopy(defs.defaults["player"])
	pdata["name"] = username
	defs.players[username] = pdata
	io.write2("","users",defs.users)
	io.write2("players",username,pdata)
	return True
def handle_login(self,data):
	if not self.check(data,"command","username","password"):
		return
	command = data["command"]
	username = data["username"]
	password = data["password"]
	if command == "register":
		if register(username,password):
			self.send_msg(201,"Success.")
		else:
			self.send_msg(401,"Username already exists.")
	elif command == "login":
		if not check_user(username):
			self.send_msg(401,"Username doesn't exist.")
		elif not check_pass(username,password):
			self.send_msg(401,"Invalid password.")
		else:
			self.send_msg(200,str(make_key(username)))
from . import defs
