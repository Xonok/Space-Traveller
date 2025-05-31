import os,json
from . import io,items,character,map,structure,ship,user,exploration

classes = {
	"items": items.SaveItems,
	"items_nosave": items.Items,
	"user": user.User,
	"character": character.Character,
	"grid": map.Grid,
	"ship": ship.Ship,
	"structure": structure.Structure,
	"system": map.System,
	"system_objects": map.SystemObjects,
	"world": map.World,
	"achievements": exploration.Achievements
}

instances = []
current_file = ""
def has_keys(table,dfields,typename):
	for key in dfields.keys():
		if key[0] == "?": continue
		if key not in table:
			raise Exception(current_file+": Key '"+key+"' missing from table of type "+typename+".")
	for key in table.keys():
		key2 = "?"+key
		if key not in dfields and key2 not in dfields:
			raise Exception(current_file+": Excess key '"+key+"' in table for type "+typename+".")
def make(data,current_type):
	parts = current_type.split(":",1)
	btype = parts[0]
	dcontent = None
	if len(parts) > 1:
		dcontent = parts[1]
	dtype = type(data).__name__
	dfields = {}
	dclass = None
	if current_type in typedefs:
		if "type" in typedefs[current_type]:
			btype = typedefs[current_type]["type"]
		elif "fields" in typedefs[current_type]:
			btype = "dict"
		else:
			btype = dtype
		if "content" in typedefs[current_type]:
			dcontent = typedefs[current_type]["content"]
		if "fields" in typedefs[current_type]:
			dfields = typedefs[current_type]["fields"]
		if "class" in typedefs[current_type]:
			dclass = typedefs[current_type]["class"]
	elif dtype != btype and btype not in ["int","float","str","dict","list"]:
		raise Exception(current_file+": Undefined type "+current_type)
	if dtype != btype and (current_type not in classes or classes[current_type] != type(data)):
		raise Exception(current_file+": Type mismatch. Data is of type '"+dtype+"' but should be "+current_type+"("+btype+")")
	if dtype == "list":
		table = []
		if current_type != "list" and dcontent:
			for value in data:
				table.append(make(value,dcontent))
		else:
			table = data
		if dclass:
			if dclass not in classes:
				raise Exception(current_file+": Class '"+dclass+"' not in classes.")
			table = classes[dclass](**table)
			for i in instances:
				i.parent = table
			instances.append(table)
		return table
	elif dtype == "dict":
		table = {}
		if current_type != "dict":
			for key,value in data.items():
				key2 = "?"+key
				if key.startswith("_"): continue
				if key in dfields.keys():
					#print("Key "+key+" in fields.")
					expected = dfields[key]
				elif key2 in dfields.keys():
					expected = dfields[key2]
				elif dcontent:
					#print("Type ("+type(key).__name__+") of key "+key+" is in pairs.")
					expected = dcontent
				else:
					raise Exception(current_file+": Invalid key '"+key+"' for type "+current_type)
				if expected == "-": continue
				table[key] = make(value,expected)
		else:
			table = data
		if len(dfields):
			has_keys(table,dfields,current_type)
		if dclass:
			if dclass not in classes:
				raise Exception(current_file+": Class '"+dclass+"' not in classes.")
			table = classes[dclass](**table)
			for i in instances:
				i.parent = table
			instances.append(table)
		return table
	else:
		#print(dtype)
		return data
def read(current_type,*path):
	global instances,current_file
	instances = []
	current_file = os.path.join("data",*path)
	table = io.read2(["data",*path])
	if table is None:
		raise Exception("File "+current_file+" is invalid or missing.")
	return make(table,current_type)
def reads(table,current_type,*path):
	global instances,current_file
	instances = []
	io.check_dir(os.path.join("data",*path,""))
	files = os.listdir(os.path.join("data",*path))
	for fname in files:
		tokens = fname.split(".")
		if tokens[-1] != "json": continue
		fname_no_ext = fname.replace(".json","")
		table2 = read(current_type,*path,fname_no_ext)
		table[fname_no_ext] = make(table2,current_type)
def read_def(current_type,*path):
	global instances,current_file
	instances = []
	current_file = os.path.join("defs",*path)
	table = io.read2(["defs",*path])
	if table is None:
		raise Exception("File "+current_file+" is invalid or missing.")
	return make(table,current_type)
def read_defs(table,current_type,*path):
	global instances,current_file
	instances = []
	io.check_dir(os.path.join("defs",*path,""))
	files = os.listdir(os.path.join("defs",*path))
	for fname in files:
		tokens = fname.split(".")
		if tokens[-1] != "json": continue
		fname_no_ext = fname.replace(".json","")
		table2 = read_def(current_type,*path,fname_no_ext)
		table[fname_no_ext] = make(table2,current_type)
def get(obj,template=None,default=None,*keys):
	if len(keys) < 1:
		raise Exception("types.get requires key parameters.")
	last = obj
	for k in keys:
		if k in last:
			last = last[k]
		else:
			if template:
				return get(template,None,default,*keys)
			return default
	return last
def copy(obj,expected_type):
	global instances
	instances = []
	data = json.loads(json.dumps(obj))
	return make(data,expected_type)

typedefs = io.read2(["defs","defs","types"])
if not len(typedefs):
	raise Exception("Typedef file is empty or invalid.")