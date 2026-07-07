import io,inspect,sys
sys.path.insert(0,"..")

import err,action,query,var
import CSV

def init(path_log,schema_path):
	var.path_log = path_log
	var.schema_path = schema_path
	schema_init(schema_path)
	action.init()
	query.init()
def schema_init(fpath):
	try:
		with open(fpath) as f:
			txt = f.readline()
			var.schema = CSV.schema_parse(txt)
			print("SCHEMA",*var.schema.keys())
	except:
		print("Failed to load schema from path",fpath)
		raise
def restore(limit=None):
	fpath = var.path_log
	if not fpath:
		print("File path not set. Use init and pass it in.")
		return
	try:
		with open(fpath,"r") as f:
			schema_line = f.readline()
			schema = CSV.schema_parse(schema_line)
			if not CSV.schema_match(schema,var.schema):
				print("Schema mismatch.")
				return
			for idx,line in enumerate(f.readlines()):
				if limit is not None and (idx+1) > limit:
					print("Stopped reading early: limit reached.")
					break
				data = CSV.parse_line(line,var.schema)
				if not data:
					raise Exception("Failed to read line.")
				run(**data,commit=False)
			if limit and limit-idx > 1:
				print("Rollback lost",limit-idx-1,"commit(s) more than it should've.")
	except:
		print("Failed to restore DB from disk.")
		raise
def rollback(idx):
	print("\nROLLBACK TO COMMIT",idx)
	var.tables = {}
	var.commands_run = 0
	restore(idx)
	CSV.truncate(var.path_log,idx)
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
	CSV.write_line(var.path_log,var.schema,**kwargs)
	#print("write",kwargs)
def run(commit=True,**kwargs):
	if err.missing(kwargs,"action"): return
	if "idx" not in kwargs:
		kwargs["idx"] = var.commands_run
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
	var.commands_run += 1
	if commit:
		write(**kwargs)
	return var.commands_run
def run_line(cmd_str,commit=True):
	print("run_line",var.schema,cmd_str)
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
