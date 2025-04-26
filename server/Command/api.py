import inspect
from server import user,defs,error,ship

commands = {}
command_auth = {}
command_args = {}

def register(cmd,func,auth=True):
	signature = inspect.signature(func)
	args = {}
	for name,param in signature.parameters.items():
		if param.default is inspect.Parameter.empty:
			args[name] = None
		else:
			args[name] = param.default
	if "ctx" not in args:
		print("Error: command "+command+" must have ctx as its first parameter.")
	else:
		if args["ctx"] is not None:
			print("Error: command "+command+" should have no default value for ctx.")
	commands[cmd] = func
	command_auth[cmd] = auth
	command_args[cmd] = args
def is_int_plus(data):
	return type(data) is int and data > 0
table = {
	"int+": is_int_plus,
}
def type_validate(typename,data):
	if type(data).__name__ == typename:
		return True
	if typename not in table:	
		print("Unknown type: "+typename)
		return False
	return table[typename](data)
def auth(name,data):
	#user.check_key returns error.Auth if it fails
	username = user.check_key(data["key"])
	udata = defs.users.get(username)
	if "char" in data and data["char"] in udata["characters"]:
		udata["active_character"] = data["char"]
		del data["char"]
	cname = udata["active_character"]
	cdata = defs.characters.get(cname)
	ctx = {
		"uname": username,
		"udata": udata,
		"cdata": cdata
	}
	if "ship" in data:
		if ship.get(data["ship"])["owner"] != cname: raise error.User("You don't own that ship.")
		cdata["ship"] = data["ship"]
		del data["ship"]
	del data["key"]
	if cdata:
		ctx["pship"] = ship.get(cdata.ship())
		ctx["pships"] = ship.gets(cdata["name"])
	return ctx
def process(self,data):
	#verify command
	self.check(data,"command")
	cmd = data.get("command")
	if cmd not in commands: return {}
	del data["command"]
	#auth
	ctx = {
		"command": cmd,
		"server": self
	}
	should_auth = command_auth[cmd]
	if should_auth:
		self.check(data,"key")
		ctx = ctx | auth(cmd,data)
	for k,v in data.items():
		if k not in command_args[cmd]:
			raise error.User("Excess parameter for command "+cmd+": "+k)
		ptype = command_args[cmd][k]
		if not type_validate(ptype,v):
			raise error.User("Wrong type for param "+k+" in command "+cmd+": "+str(v)+" needs to be of type: "+ptype)
	missing = []
	for k,v in command_args[cmd].items():
		if k == "ctx": continue
		if k not in data:
			missing.append(k)
	if len(missing):
		raise error.User("Missing params for command "+cmd+": "+str(missing))
	response = commands[cmd](ctx,**data)
	if not response:
		return {}
	return response
