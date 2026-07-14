import json,os

data = {}
data_to_check = {}

#Explanation of check_omissions parameter:
FIX_OMISSIONS = True
REPORT_OMISSIONS = False

def read(name,check_omissions=None):
	try:
		raw = None
		with open(os.path.join("config",name+".json"),"r") as f:
			raw = f.read()
		result = json.loads(raw)
		if check_omissions is not None:
			default = None
			with open(os.path.join("config","default",name+".json"),"r") as f:
				default = json.load(f)
			merged = default | result
			new_raw = json.dumps(merged)
			additions = 0
			for k,v in default.items():
				if k not in result:
					print("Key",k,"missing in config",name)
					if check_omissions == FIX_OMISSIONS:
						print("Using default for that key.")
						additions += 1
						result[k] = v
			if additions:
				print("Overwriting config '"+name+"' due to adding default values.")
				with open(os.path.join("config",name+".json"),"w") as f:
					json.dump(result,f,indent="\t")
		return result
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
		check_omissions = data_to_check.get(root)
		data[root] = read(root,check_omissions=check_omissions)
		count += 1
	print("Configs successfully read:",count)
def get(name):
	return data.get(name)
def no_omissions(name,use_defaults=False):
	data_to_check[name] = use_defaults