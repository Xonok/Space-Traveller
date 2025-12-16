import os,json,_thread,queue,csv,hashlib,copy
from . import config

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
def do_write2(path,table,old_path,force=False):
	if not config.config["saving"] and not force: return
	check_dir(path)
	table_copy = copy.deepcopy(table)
	data = json.dumps(table_copy,indent="\t")
	with open(path+"_temp","w+") as f:
		f.write(data)
		if os.name != "nt":
			f.flush()
			os.fsync(f.fileno())
	if path != old_path:
		table.old_name = None
		if os.path.exists(old_path):
			os.remove(old_path)
	os.replace(path+"_temp",path)
	if os.name != "nt":
		dir_fd = os.open(os.path.dirname(path), os.O_DIRECTORY)
		os.fsync(dir_fd)
		os.close(dir_fd)
def do_write_csv(path,table,force=False):
	if not config.config["saving"] and not force: return
	check_dir(path)
	with open(path,"a",newline="",encoding="utf-8") as f:
		writer = csv.writer(f)
		writer.writerow(table)
		f.flush()
		os.fsync(f.fileno())
def do_delete(path,table,force=False):
	if not config.config["saving"] and not force: return
	check_dir(path)
	if getattr(table,"deleted",False) == True:
		if os.path.exists(path):
			os.remove(path)
def write_log(txt,*path):
	path = os.path.join("log",*path)
	check_dir(path)
	with open(path,"a+") as f:
		f.write(txt)
def do_writes():
	global counta,countb
	while True:
		todo = {}
		path,table,old,mode = cached_writes.get()
		if path not in todo:
			todo[path] = (table,old,mode)
		while cached_writes.qsize():
			path,table,old,mode = cached_writes.get()
			if path not in todo:
				todo[path] = (table,old,mode)
		for key,value in todo.items():
			table,old,mode = value
			if mode == "json":
				do_write2(key,table,old)
			elif mode == "csv":
				do_write_csv(key,table)
			elif mode == "delete":
				do_delete(key,table)
			else:
				raise Exception("Unknown writing mode: "+str(mode))
			countb += 1
		#print(counta,countb)
def write2(dir,path,table,old_path=None):
	global counta
	if not path:
		raise Exception("No path provided to IO.")
	if not old_path:
		old_path = path
	path = os.path.join("data",dir,path+".json")
	old = os.path.join("data",dir,old_path+".json")
	cached_writes.put((path,table,old,"json"))
	counta += 1
def csv_append(dir,path,data):
	global counta
	if not path:
		raise Exception("No path provided to IO.")
	path = os.path.join("data",dir,path+".csv")
	cached_writes.put((path,data,path,"csv"))
	counta += 1
def read2(path,constructor=dict):
	if not path:
		raise Exception("No path provided to IO.")
	try:
		path = os.path.join(*path)+".json"
		with open(path,"r",encoding="utf-8") as f:
			return json.loads(f.read(),object_hook=lambda d: constructor(**d))
	except json.JSONDecodeError:
		print("Path: "+path)
		raise
def checksum(path):
	if not path:
		raise Exception("No path provided to IO.")
	path = os.path.join(*path)+".json"
	with open(path,"r",encoding="utf-8") as f:
		return hashlib.sha256(json.dumps(f.read()).encode()).hexdigest()
def read_csv(*path):
	if not path:
		raise Exception("No path provided to IO.")
	path = os.path.join(*path)+".csv"
	with open(path,"r",newline="",encoding="utf-8") as f:
		reader = csv.reader(f)
		return list(reader)
def delete(table,*args):
	setattr(table,"deleted",True)
	path = os.path.join(*args)
	cached_writes.put((path,table,path,"delete"))
def get_file_data(path,mode="rb",encoding=None):
	check_dir(path)
	if not os.path.exists(path):
		raise Exception("No file called: "+path)
	with open(path,mode,encoding=encoding) as f:
		return f.read()
def get_file_name(path):
	return os.path.basename(path)
def ensure(path,default):
	path = os.path.join("data",path+".json")
	if not os.path.exists(path):
		do_write2(path,default,path,True)
def init():
	_thread.start_new_thread(do_writes,())