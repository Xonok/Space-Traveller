import inspect
from server import defs,ship

commands = {}
queries = {}
def register_command(name,*qnames):
	if name in commands:
		raise Exception("Command "+name+" registered twice.")
	for q in qnames:
		if q not in queries:
			raise Exception("Query "+q+" not registered.")
	commands[name] = qnames
def register_query(name,func):
	if name in queries:
		raise Exception("Query "+name+" registered twice.")
	queries[name] = func
def process_command(name,msg,udata,cdata=None):
	ctx = {
		"udata": udata,
		"cdata": cdata
	}
	if cdata:
		ctx["pship"] = ship.get(cdata.ship())
		ctx["pships"] = ship.gets(cdata["name"])
	if name in commands:
		cmd_data = commands[name]
		for q in cmd_data:
			if q not in queries:
				raise Exception("Unknown query "+q+" for command "+name)
			if q in msg:
				raise Exception("Query "+q+" called twice(command:"+name+")")
			signature = inspect.signature(queries[q])
			args = {}
			for name in signature.parameters:
				args[name] = ctx[name]
			msg[q] = queries[q](**args)
	for k,v in ctx.items():
		if k in ["cdata","pship","pships"]:
			msg[k] = v
	if "pship" in msg:
		msg["checksum_map"] = defs.systems[msg["pship"]["pos"]["system"]].checksum