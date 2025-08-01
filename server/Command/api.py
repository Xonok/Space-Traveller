import inspect,time,math,builtins
from server import user,defs,error,ship,character,spawner,gathering,Character,structure,Query,Battle,Entity

commands = {}
command_auth = {}
command_args = {}
#special args are only checked in auth
#for now that's fine because the functions need auth anyway
special_args = {}
pre_funcs = []

#HUGE performance hit - spawners are ticked every time anyone does anything

#special arg funcs
def update_active_char(val,udata):
	if val in udata["characters"]:
		udata["active_character"] = val
def update_active_ship(val,udata):
	cname = udata["active_character"]
	cdata = defs.characters.get(cname)
	if ship.get(val)["owner"] != cname: raise error.User("You don't own that ship.")
	cdata["ship"] = val
#pre_funcs
def tick_character(udata):
	cname = udata["active_character"]
	cdata = defs.characters.get(cname)
	if not cdata: return
	pship = ship.get(cdata.ship())
	for ps in ship.gets(cdata["name"]).values():
		ps.tick()
	pship.get_room()
	Character.update_command_slots(cdata)
	pship.save()
	cdata.save()
def tick_spawners():
	spawner.tick()
def tick_tile(pship):
	psystem,px,py = pship.loc()
	gathering.update_resources(psystem,px,py)
	Entity.landmark.update(psystem,px,py)
def tick_structure(pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if tstructure:
		tstructure.tick()
		tstructure.make_ships()

def check_param_type(cmd,name):
	if ":" in name:
		tokens = name.split(":")
		name = tokens.pop()
		for token in tokens:
			if token not in ["list","dict"]:
				print("Unknown container type: "+token)
	if getattr(builtins,name,None) is None and name not in table_types:
		print("Command: Unknown parameter type "+name+" for command "+cmd)
def register(cmd,func,*q_args):
	signature = inspect.signature(func)
	args = {}
	auth = False
	for name,param in signature.parameters.items():
		if param.default is inspect.Parameter.empty:
			args[name] = None
		else:
			check_param_type(name,param.default)
			args[name] = param.default
		if name == "ctx":
			raise Exception("Command "+cmd+" should not require ctx.")
		if name in special_args:
			raise Exception("Command "+cmd+" requires "+name+" but that's a special argument that no command can use directly.")
		if name in ["uname","udata","cname","cdata","pship","pships"]:
			auth = True
	commands[cmd] = func
	command_auth[cmd] = auth
	command_args[cmd] = args
	Query.register_command(cmd,*q_args)
def add_prefunc(func):
	signature = inspect.signature(func)
	for name in signature.parameters:
		if name not in ["uname","udata","cdata","pship","pships"]:
			raise Exception("Unknown param for prefunc: "+name)
	pre_funcs.append(func)
def is_int_plus(data):
	return type(data) is int and data >= 0
table_types = {
	"int+": is_int_plus,
}
def type_validate(typename,data):
	if ":" in typename:
		outer,inner = typename.split(":",1)
		result = True
		if outer == "list":
			for el in data:
				if not type_validate(inner,el):
					result = False
		if outer == "dict":
			for val in data.values():
				if not type_validate(inner,val):
					result = False
		return result
	if type(data).__name__ == typename:
		return True
	if typename not in table_types:	
		print("Unknown type: "+typename)
		return False
	return table_types[typename](data)
def process(server,data):
	now = time.time()
	#verify command
	server.check(data,"command")
	cmd = data.get("command")
	del data["command"]
	idata_hash = data.get("idata_hash")
	if idata_hash:
		del data["idata_hash"]
	shipdefs_hash = data.get("shipdefs_hash")
	if shipdefs_hash:
		del data["shipdefs_hash"]
	ctx = {
		"command": cmd,
		"server": server
	}
	should_auth = command_auth.get(cmd,True)
	if should_auth:
		server.check(data,"key")
		uname = server.auth(data["key"])
		udata = defs.users.get(uname)
		ctx = ctx | {
			"uname": uname,
			"udata": udata
		}
		del data["key"]
	#Update active character and active ship
	if "udata" in ctx:
		for arg in special_args:
			if arg in data:
				special_args[arg](data[arg],ctx["udata"])
				del data[arg]
		cname = ctx["udata"]["active_character"]
		cdata = defs.characters.get(cname)
		ctx["cname"] = cname
		ctx["cdata"] = cdata
		server.user = ctx["uname"]
		server.char = ctx["cname"]
		if cdata:
			ctx["pship"] = ship.get(cdata.ship())
			ctx["pships"] = ship.gets(cdata["name"])
	#Various preprocessing. E.g. ship ticks, tile ticks,
	#...or even every spawner in the universe for some reason
	if should_auth:
		for func in pre_funcs:
			args = {}
			signature = inspect.signature(func)
			missing_params = False
			for name in signature.parameters:
				if name not in ctx:
					if name not in ["command","server","uname","udata","cname","cdata","pship","pships"]:
						raise Exception("Prefunc function requires parameter "+name+" but ctx doesn't ever have it.")
					missing_params = True
					continue
				args[name] = ctx[name]
			if not missing_params:
				func(**args)
	if should_auth and cmd is None and ctx["cdata"] is None:
		raise error.Char()
	if cmd not in commands: raise error.User("Unknown command: "+cmd)
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
			if ctx[k] is None:
				if k == "cdata":
					raise error.Char()
		if k in data:
			input[k] = data[k]
		if k == "ctx":
			input[k] = ctx
	if len(missing):
		raise error.User("Missing params for command "+cmd+": "+str(missing))
	response = commands[cmd](**input)
	if not response:
		response = {}
	udata = ctx.get("udata")
	cdata = ctx.get("cdata")
	Query.process_command(cmd,response,udata,cdata)
	character_active = False
	for arg in ["cdata","pship","pships"]:
		if arg in command_args[cmd]:
			character_active = True
	if character_active:
		response["in_battle"] = Battle.get(cdata) is not None
		character.update_active(cdata)
		user.update_active(udata,server)
		if idata_hash != defs.idata_hash:
			response["idata_hash"] = defs.idata_hash
			response["idata"] = defs.full_idata
	msgs = server.get_messages()
	response["messages"] = msgs
	later = time.time()
	d_t = later-now
	print(cmd+":"+str(math.floor(d_t*1000))+"ms")
	response["accept_time"] = now
	response["response_time"] = later
	return response

special_args["active_character"] = update_active_char
special_args["active_ship"] = update_active_ship

add_prefunc(tick_character)
add_prefunc(tick_spawners)
add_prefunc(tick_tile)