import os,json,_thread,queue
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
	if getattr(table,"deleted",False) == True:
		if os.path.exists(path):
			os.remove(path)
	else:
		with open(path+"_temp","w+") as f:
			f.write(json.dumps(table,indent="\t"))
		if path != old_path:
			table.old_name = None
		if os.path.exists(old_path):
			os.remove(old_path)
		if os.path.exists(path):
			os.remove(path)
		os.rename(path+"_temp",path)
def write_log(txt,*path):
	path = os.path.join("log",*path)
	check_dir(path)
	with open(path,"a+") as f:
		f.write(txt)
def do_writes():
	global counta,countb
	while True:
		todo = {}
		path,table,old = cached_writes.get()
		if path not in todo:
			todo[path] = (table,old)
		while cached_writes.qsize():
			path,table,old = cached_writes.get()
			if path not in todo:
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
	path = os.path.join("data",dir,path+".json")
	old = os.path.join("data",dir,old_path+".json")
	cached_writes.put((path,table,old))
	counta += 1
def read(*args):
	path = os.path.join("server",*args)
	with open(path,"r") as f:
		return f.read()
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
def delete(table,*args):
	setattr(table,"deleted",True)
	path = os.path.join(*args)
	cached_writes.put((path,table,path))
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