import os,json,_thread,time,queue

cwd = os.getcwd()
cached_writes = queue.Queue()
counta = 0
countb = 0

def check_dir(path):
	path = os.path.dirname(path)
	if not os.path.exists(path):
		os.makedirs(path)
def do_write2(path,table):
	check_dir(path)
	with open(path+"_temp","w+") as f:
		f.write(json.dumps(table,indent="\t"))
	if os.path.exists(path):
		os.remove(path)
	os.rename(path+"_temp",path)
def do_writes():
	global counta,countb
	while True:
		todo = {}
		path,table = cached_writes.get()
		todo[path] = table
		while cached_writes.qsize():
			path,table = cached_writes.get()
			todo[path] = table
		for key,value in todo.items():
			do_write2(key,value)
			countb += 1
		#print(counta,countb)
def write2(dir,path,table):
	global counta
	if not path:
		raise Exception("No path provided to IO.")
	path = os.path.join("server","data",dir,path+".json")
	cached_writes.put((path,table))
	counta += 1
def read2(dir,path,default=dict):
	if not path:
		raise Exception("No path provided to IO.")
	try:
		path = os.path.join("server","data",dir,path+".json")
		with open(path,"r") as f:
			return json.loads(f.read(),object_hook=lambda d: default(**d))
	except:
		return default()
def get_file_data(path):
	path = os.path.join("data",path)
	check_dir(path)
	with open(path,"rb") as f:
		return f.read()
_thread.start_new_thread(do_writes,())