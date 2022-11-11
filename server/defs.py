from . import io,items,types,user
def read(name):
	return io.read2("defs",name)
def make_dict(keys,folder,typename):
	table = {}
	for e in keys:
		table[e] = types.read(folder,e,typename)
	return table

#Constants
items = types.read("defs","items","item_types")
ships = types.read("defs","ships","ship_types")
planets = read("planets")
industries = read("industries")
machines = read("machines")
defaults = read("defaults")
if not len(defaults):
	raise Exception("Defaults file(defs/defaults.json) missing or invalid.")
for key,value in defaults.items():
	print(key,value)
	defaults[key] = types.make(value,key)

#Mutable
players = make_dict(user.get_all(),"players","player")
systems = {}
systems["Ska"] = types.read("systems","Ska","system")
structures = {}
objects = {}
for system in systems.values():
	for tile in system["tiles"].get_all():
		if "structure" in tile:
			tstruct = tile["structure"]
			structures[tstruct] = types.read("structures",tstruct,"structure")
		if "object" in tile:
			tstruct = tile["object"]
			objects[tstruct] = types.read("objects",tstruct,"object")
