import os,json

cwd = os.getcwd()

def check_dir(path):
	path = os.path.dirname(path)
	if not os.path.exists(path):
		os.makedirs(path)
def write(dir,path,table):
	if not path:
		raise Exception("No path provided to IO.")
	path = os.path.join("server","data",dir,path+".json")
	check_dir(path)
	with open(path,"w+") as f:
		f.write(json.dumps(table))
def read(dir,path,default=dict):
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
