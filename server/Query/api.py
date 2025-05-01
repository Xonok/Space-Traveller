import inspect

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
	if name not in commands:
		return
	cmd_data = commands[name]
	ctx = {
		"udata": udata,
		"cdata": cdata
	}
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
