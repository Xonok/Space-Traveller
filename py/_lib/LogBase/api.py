import io,inspect,sys,queue,_thread,shutil,os,collections,datetime
sys.path.insert(0,"..")

from . import err,action,query,var
import CSV

def init(path_log,schema_path):
	var.path_log = path_log
	var.schema_path = schema_path
	var.write_buffer = queue.Queue()
	var.write_lock = _thread.allocate_lock()
	schema_init(schema_path)
	action.init()
	query.init()
	_thread.start_new_thread(loop_write,())
	
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
def loop_write():
	run = True
	while run:
		data = var.write_buffer.get()
		var.write_lock.acquire()
		while data:
			CSV.write_entry(var.path_log,var.schema,**data)
			try:
				data = var.write_buffer.get_nowait()
			except queue.Empty:
				print("Empty queue error. No problem.")
				break
		var.write_lock.release()
def write(**kwargs):
	#Writing happens on a separate thread, because waiting after disk for everything would be silly.
	var.write_buffer.put(kwargs)
	#CSV.write_entry(var.path_log,var.schema,**kwargs)
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
	#Issue: writing to log should be first and THAT should trigger running the command.
	#But then every command would have disk latency...
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
	#Note: this should be called on a separate thread since file IO has to wait after disk.

	#stop saving to disk(still accept writes,just buffer them)
	var.write_lock.acquire()
	
	#move old log to backup folder
	date_now = datetime.datetime.now()
	datestring = date_now.strftime("%Y-%m-%d_%H:%M:%S")
	path_backup = os.path.join(folder_backup,datestring+"_"+var.path_log)
	dir_backup = os.path.dirname(path_backup)
	if not os.path.exists(dir_backup):
		os.makedirs(dir_backup)
	shutil.move(var.path_log,path_backup)
	
	#read all entries from old log, only keep the newest of each kind.
	data = collections.OrderedDict()
	with open(path_backup,"r") as f:
		#table_create	- table
		#table_delete	- table
		#table_set		- table, key, val
		#table_unset	- table, key
		for line in f.readlines():
			action,table,key,val = CSV.tokenize(line)
			if action == "table-unset":
				#Purposefully cause a collision, so that unset would overwrite set.
				ref = "table-set,"+table
			else:
				ref = action+","+table
			if key:
				ref += ","+key
			#Don't overwrite. Need to delete and readd, so the new entry would be at the end.
			if ref in data:
				del data[ref]
			data[ref] = (action,table,key,val)
	
	#Clean up entries. If a table was deleted, any operations on it before that don't matter. (major optimization)
	keys_processed = []
	for ref,value in list(data.items()):
		action,table,key,val = value
		if action == "table-delete":
			for ref2 in list(keys_processed):
				action2,table2,key2,val2 = data[ref2]
				if table == table2:
					del data[ref2]
					keys_processed.remove(ref2)
		keys_processed.append(ref)
	
	#Start a new log and write the previous data to it.
	with open(var.path_log,"a+") as f:
		for entry in data.values():
			action,table,key,val = entry
			#By the "as if" rule, if the last operation on something was "unset" or "delete", we can safely leave it out.
			if action == "table-unset": continue
			if action == "table-delete": continue
			CSV.write_line_file(f,action,table,key,val)
	
	#temporary cleanup to ease testing
	#shutil.move(path_backup,var.path_log)
	var.write_lock.release()
def log_idx():
	return var.log_idx
