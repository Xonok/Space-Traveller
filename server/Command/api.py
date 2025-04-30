import inspect,time,math
from server import user,defs,error,ship,character

commands = {}
command_auth = {}
command_args = {}
#special args are only checked in auth
#for now that's fine because the functions need auth anyway
special_args = {}

def update_active_char(val,data,udata):
	if val in udata["characters"]:
		udata["active_character"] = val
def update_active_ship(val,data,udata):
	cname = udata["active_character"]
	cdata = defs.characters.get(cname)
	if ship.get(val)["owner"] != cname: raise error.User("You don't own that ship.")
	cdata["ship"] = val
def register(cmd,func,auth=True):
	signature = inspect.signature(func)
	args = {}
	for name,param in signature.parameters.items():
		if param.default is inspect.Parameter.empty:
			args[name] = None
		else:
			args[name] = param.default
		if name == "ctx":
			raise Exception("Command "+cmd+" should not require ctx.")
		if name in special_args:
			raise Exception("Command "+cmd+" requires "+name+" but that's a special argument that no command can use directly.")
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
def auth(self,data):
	#self is only used for getting client IP.
	#user.check_key returns error.Auth if it fails
	username = user.check_key(data["key"])
	udata = defs.users.get(username)	
	for arg in special_args:
		if arg in data:
			special_args[arg](data[arg],data,udata)
			del data[arg]
	cname = udata["active_character"]
	cdata = defs.characters.get(cname)
	ctx = {
		"uname": username,
		"udata": udata,
		"cdata": cdata
	}
	del data["key"]
	if cdata:
		ctx["pship"] = ship.get(cdata.ship())
		ctx["pships"] = ship.gets(cdata["name"])
	return ctx
def process(self,data):
	#verify command
	self.check(data,"command")
	cmd = data.get("command")
	del data["command"]
	ctx = {
		"command": cmd,
		"server": self
	}
	should_auth = command_auth.get(cmd,True)
	if should_auth:
		self.check(data,"key")
		ctx = ctx | auth(self,data)
	if cmd not in commands: return {}
	now = time.time()
	#auth
	for k,v in data.items():
		if k not in command_args[cmd]:
			raise error.User("Excess parameter for command "+cmd+": "+k)
		ptype = command_args[cmd][k]
		if not type_validate(ptype,v):
			raise error.User("Wrong type for param "+k+" in command "+cmd+": "+str(v)+" needs to be of type: "+ptype)
	missing = []
	input = {}
	for k,v in command_args[cmd].items():
		if k not in data and k not in ctx and k != "ctx":
			missing.append(k)
			continue
		if k in ctx and k in data:
			raise error.User("Parameter "+k+" for command "+cmd+" should not be provided by client.")
		if k in ctx:
			input[k] = ctx[k]
		if k in data:
			input[k] = data[k]
		if k == "ctx":
			input[k] = ctx
	if len(missing):
		raise error.User("Missing params for command "+cmd+": "+str(missing))
	response = commands[cmd](**input)
	later = time.time()
	d_t = later-now
	print(cmd+":"+str(math.floor(d_t*1000))+"ms")
	if not response:
		return {}
	return response

special_args["active_character"] = update_active_char
special_args["active_ship"] = update_active_ship