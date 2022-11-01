from . import io,items,player,grid,structure,object

classes = {
	"items": items.SaveItems,
	"player": player.Player,
	"grid": grid.Grid,
	"structure": structure.Structure,
	"object": object.Object
}

instances = []
def has_keys(table,dfields,typename):
	for key in dfields.keys():
		if key[0] == "?": return
		if not key in table:
			raise Exception("Key "+key+" missing from table of type "+typename+".")
	for key in table.keys():
		key2 = "?"+key
		if not key in dfields and not key2 in dfields:
			raise Exception("Excess key "+key+" in table for type "+typename+".")
def make(data,current_type):
	btype = current_type
	dtype = type(data).__name__
	dpairs = ["",""]
	dfields = {}
	dclass = None
	if current_type in typedefs:
		if "type" in typedefs[current_type]:
			btype = typedefs[current_type]["type"]
		else:
			btype = "dict"
		if "pairs" in typedefs[current_type]:
			dpairs = typedefs[current_type]["pairs"]
		if "fields" in typedefs[current_type]:
			dfields = typedefs[current_type]["fields"]
		if "class" in typedefs[current_type]:
			dclass = typedefs[current_type]["class"]
	if dtype != btype:
		raise Exception("Type mismatch. Data is of type "+dtype+" but should be "+current_type+"("+btype+")")
	if dtype == "dict":
		table = {}
		if current_type != "dict":
			for key,value in data.items():
				expected = None
				key2 = "?"+key
				if key in dfields.keys():
					#print("Key "+key+" in fields.")
					expected = dfields[key]
				elif key2 in dfields.keys():
					expected = dfields[key2]
				elif type(key).__name__ == dpairs[0]:
					#print("Type ("+type(key).__name__+") of key "+key+" is in pairs.")
					expected = dpairs[1]
				else:
					raise Exception("Invalid key "+key+" for type "+current_type)
				table[key] = make(value,expected)
		if len(dfields):
			has_keys(table,dfields,current_type)
		if dclass:
			if dclass not in classes:
				raise Exception("Class "+dclass+" not in classes.")
			table = classes[dclass](**table)
			for i in instances:
				i.parent = table
			instances.append(table)
		return table
	else:
		#print(dtype)
		return data
def read(dir,path,current_type):
	global instances
	instances = []
	table = io.read2(dir,path)
	if not len(table):
		raise Exception("File "+dir+"/"+path+" is empty or invalid.")
	return make(table,current_type)

typedefs = io.read2("defs","types")
if not len(typedefs):
	raise Exception("Typedef file is empty or invalid.")
