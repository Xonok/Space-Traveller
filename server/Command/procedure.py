from server import user,defs

commands = {}
command_auth = {}
def command(name,func,auth=True):
	commands[name] = func
	command_auth[name] = auth
def auth(self,name,data):
	#user.check_key returns error.Auth if it fails
	username = user.check_key(data["key"])
	udata = defs.users.get(username)
	ctx = {
		"udata": user.check_key(data["key"]),
		"cdata": defs.characters.get(udata["active_character"]),
		"self": self
	}
	return ctx
def process(self,data):
	#verify command
	self.check(data,"command")
	name = data.get("command")
	if name not in commands: return
	#auth
	ctx = None
	should_auth = command_auth[name]
	if should_auth:
		self.check(data,"key")
		ctx = auth(self,name,data)
	response = commands[name](self,data,ctx)
	if not response:
		return {}
	return response
