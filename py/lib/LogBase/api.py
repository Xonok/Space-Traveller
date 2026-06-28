import io,inspect

import err,action,query

commands = {}
command_args = {}

queries = {}
query_args = {}

def init():
	action.init()
	query.init()
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
def restore(fname):
	global tables
	try:
		with open(fname,"r") as f:
			schema_keys = csv_split(f.readline())
			schema_table = {}
			for idx,key in enumerate(schema_keys):
				schema_table[key] = idx
			for line in f.readlines():
				tokens = csv_split(line)
				data = {}
				for key,idx in schema_table.items():
					data[key] = tokens[idx]
				#action,table,ref,data = tokens
				#print(data)
				run(**data,commit=False)
	except:
		print("Failed to restore DB from disk.")
		raise
def action_register(name,func):
	if name in commands:
		print("Duplicate command:",name)
		return
	if not func:
		print("func not provided")
	commands[name] = func
	spec = inspect.signature(func).parameters
	command_args[name] = list(spec)
def query_register(name,func):
	if name in queries:
		print("Duplicate query:",name)
		return
	if not func:
		print("func not provided")
	queries[name] = func
	spec = inspect.signature(func).parameters
	query_args[name] = list(spec)
def require(data,*args):
	err = False
	for a in args:
		if a not in data:
			print("Required arg",a,"not in data")
			err = True
	return err
def run(commit=False,**kwargs):
	if err.missing(kwargs,"action"): return
	action = kwargs["action"]
	if action not in commands:
		print("Unknown action",action)
		return
	args_in = {}
	args = command_args[action]
	for k,v in kwargs.items():
		if k in args:
			args_in[k] = v
	#print(args_in)
	commands[action](**args_in)
	if commit:
		write(action,table,ref,data)
def ask(**kwargs):
	if err.missing(kwargs,"query"): return
	query = kwargs["query"]
	if query not in queries:
		print("Unknown query",query)
		return
	args_in = {}
	args = query_args[query]
	for k,v in kwargs.items():
		if k in args:
			args_in[k] = v
	#print(args_in)
	return queries[query](**args_in)
