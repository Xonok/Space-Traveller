import os,json

cwd = os.getcwd()

def check_dir(path):
	path = os.path.join("data",path)
	path = os.path.dirname(path)
	if not os.path.exists(path):
		os.makedirs(path)
def write(path,table):
	check_dir(path)
	path = os.path.join("data",path)
	with open(path,"w+") as f:
		f.write(json.dumps(table))
def read(path):
	try:
		path = os.path.join("data",path)
		with open(path,"r") as f:
			return json.loads(f.read())
	except:
		return {}
def get_file_data(path):
	path = os.path.join("data",path)
	check_dir(path)
	with open(path,"rb") as f:
		return f.read()