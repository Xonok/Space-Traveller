import os,json,_thread,queue

cwd = os.getcwd()
cached_writes = queue.Queue()
counta = 0
countb = 0

def clear_writes():
	cached_writes.queue.clear()
def check_dir(path):
	path = os.path.dirname(path)
	if not os.path.exists(path):
		os.makedirs(path)
def do_write2(path,table,old_path):
	check_dir(path)
	with open(path+"_temp","w+") as f:
		f.write(json.dumps(table,indent="\t"))
	if path != old_path:
		table.old_name = None
	if os.path.exists(old_path):
		os.remove(old_path)
	os.rename(path+"_temp",path)
def do_writes():
	global counta,countb
	while True:
		todo = {}
		path,table,old = cached_writes.get()
		todo[path] = (table,old)
		while cached_writes.qsize():
			path,table,old = cached_writes.get()
			todo[path] = (table,old)
		for key,value in todo.items():
			do_write2(key,value[0],value[1])
			countb += 1
		#print(counta,countb)
def write2(dir,path,table,old_path=None):
	global counta
	if not path:
		raise Exception("No path provided to IO.")
	if not old_path:
		old_path = path
	path = os.path.join("server","data",dir,path+".json")
	old = os.path.join("server","data",dir,old_path+".json")
	cached_writes.put((path,table,old))
	counta += 1
def read(*args):
	path = os.path.join("server",*args)
	with open(path,"r") as f:
		return f.read()
def read2(dir,path,constructor=dict):
	if not path:
		raise Exception("No path provided to IO.")
	try:
		path = os.path.join("server","data",dir,path+".json")
		with open(path,"r") as f:
			return json.loads(f.read(),object_hook=lambda d: constructor(**d))
	except json.JSONDecodeError:
		print("Path: "+path)
		raise
def get_file_data(path):
	path = os.path.join("data",path)
	check_dir(path)
	with open(path,"rb") as f:
		return f.read()
def get_file_name(path):
	return os.path.basename(path)
_thread.start_new_thread(do_writes,())