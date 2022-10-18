import hashlib,random
from . import io

users = io.read("","users")
user_key = io.read("","user_keys")
key_user = io.read("","key_users")

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
			io.write("","user_keys",user_key)
			io.write("","key_users",key_user)
			return key
def check_user(username):
	return username in users
def check_pass(username,password):
	return users[username] == encode(username,password)
def check_key(key):
	if key in key_user:
		return key_user[key]
def register(username,password):
	if check_user(username):
		return False
	users[username] = encode(username,password)
	io.write("","users",users)
	return True
def get_all():
	return users.keys()