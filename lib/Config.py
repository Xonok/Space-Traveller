import json,os

data = {}

def read(name):
	try:
		with open(os.path.join("config",name+".json"),"r") as f:
			return json.load(f)
	except FileNotFoundError:
		print("No config called "+name+".json found. Creating a new one with default settings.")
		with open(os.path.join("config","default",name+".json"),"r") as f:
			config_str = f.read()
			with open(os.path.join("config",name+".json"),"w") as f:
				f.write(config_str)
			return json.loads(config_str)
def read_all():
	fnames = os.listdir(os.path.join(".","config","default"))
	count = 0
	for fname in fnames:
		root,ext = os.path.splitext(fname)
		data[root] = read(root)
		count += 1
	print("Configs successfully read:",count)
def get(name):
	return data.get(name)
