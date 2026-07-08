import io,inspect,sys
sys.path.insert(0,"..")

from . import err,action,query,var
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
	var.log_idx = 0
	restore(idx)
	CSV.truncate(var.path_log,idx+1)
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
def run(action,table,key=None,val=None,commit=True):
	if action == None:
		print("Missing arg: action")
		return
	if table == None:
		print("Missing arg: table")
		return
	if action not in var.commands:
		print("Unknown action",action)
		return
	args_in = {}
	args = var.command_args[action]
	if "action" in args:
		args_in["action"] = action
	if "table" in args:
		args_in["table"] = table
	if "key" in args:
		args_in["key"] = key
	if "val" in args:
		args_in["val"] = val
	var.commands[action](**args_in)
	var.log_idx += 1
	if commit:
		write(action=action,table=table,key=key,val=val)
	return var.log_idx
def ask(query,table,key=None):
	if query is None:
		print("Missing arg: query")
		return
	if query not in var.queries:
		print("Unknown query",query)
		return
	args_in = {}
	args = var.query_args[query]
	if "query" in args:
		args_in["query"] = query
	if "table" in args:
		args_in["table"] = table
	if "key" in args:
		args_in["key"] = key
	#print(args_in)
	return var.queries[query](**args_in)
def log_rotate(folder_backup):
	pass
	#pause, then dump - stalls everything until it's done, but maybe if it's once per day it can be fine.
	#pause writing
	#generate gist
	#move log to backup folder
	#make new log file
	#write gist to log
	#unpause
def log_idx():
	return var.log_idx
