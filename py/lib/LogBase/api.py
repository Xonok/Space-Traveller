import io,inspect

import err,action,query,var

def init(log_path,schema_path):
	var.log_path = log_path
	schema_init(schema_path)
	action.init()
	query.init()
def schema_init(fpath):
	try:
		with open(fpath) as f:
			txt = f.readline()
			tokens = csv_split(txt)
			if tokens[0] == None:
				print("Schema is empty.")
				return
			var.schema = tokens
			print("SCHEMA",*var.schema)
	except:
		print("Failed to load schema from path",fpath)
		raise
def csv_split(txt):
	length = len(txt)
	tokens = []
	prev = 0
	cur = 0
	in_str = False
	while(cur < length):
		c = txt[cur:cur+1]
		if c == "\"":
			in_str = not in_str
		if c == "," and not in_str:
			tokens.append(txt[prev:cur])
			prev = cur+1
		cur += 1
	if txt.endswith("\n"):
		tokens.append(txt[prev:cur-1])
	else:
		tokens.append(txt[prev:cur])
	for idx,t in enumerate(tokens):
		if t == "":
			tokens[idx] = None
		if t.startswith("\"") and t.endswith("\""):
			tokens[idx] = tokens[idx][1:-1]
	return tokens
def restore():
	fpath = var.log_path
	if not fpath:
		print("File path not set. Use init and pass it in.")
		return
	try:
		with open(fpath,"r") as f:
			schema_keys = csv_split(f.readline())
			schema_table = {}
			for idx,key in enumerate(schema_keys):
				schema_table[key] = idx
			for line in f.readlines():
				tokens = csv_split(line)
				data = {}
				for key,idx in schema_table.items():
					data[key] = tokens[idx]
				run(**data,commit=False)
	except:
		print("Failed to restore DB from disk.")
		raise
def action_register(name,func):
	if name in var.commands:
		print("Duplicate command:",name)
		return
	if not func:
		print("func not provided")
	var.commands[name] = func
	spec = inspect.signature(func).parameters
	var.command_args[name] = list(spec)
def query_register(name,func):
	if name in var.queries:
		print("Duplicate query:",name)
		return
	if not func:
		print("func not provided")
	var.queries[name] = func
	spec = inspect.signature(func).parameters
	var.query_args[name] = list(spec)
def require(data,*args):
	err = False
	for a in args:
		if a not in data:
			print("Required arg",a,"not in data")
			err = True
	return err
def write(**kwargs):
	print("write",kwargs)
def run(commit=True,**kwargs):
	if err.missing(kwargs,"action"): return
	action = kwargs["action"]
	if action not in var.commands:
		print("Unknown action",action)
		return
	args_in = {}
	args = var.command_args[action]
	for k,v in kwargs.items():
		if k in args:
			args_in[k] = v
	#print(args_in)
	var.commands[action](**args_in)
	if commit:
		write(**kwargs)
def ask(**kwargs):
	if err.missing(kwargs,"query"): return
	query = kwargs["query"]
	if query not in var.queries:
		print("Unknown query",query)
		return
	args_in = {}
	args = var.query_args[query]
	for k,v in kwargs.items():
		if k in args:
			args_in[k] = v
	#print(args_in)
	return var.queries[query](**args_in)
