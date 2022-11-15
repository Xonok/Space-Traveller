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
quests = types.read("defs","quests","quest_types")
ships = types.read("defs","ships","ship_types")
station_kits = types.read("defs","station_kits","station_kit_types")
planets = read("planets")
industries = read("industries")
machines = read("machines")
blueprints = types.read("defs","blueprints","blueprint_types")
if not len(blueprints):
	raise Exception("Blueprints file(defs/blueprints.json) missing or invalid.")
defaults = read("defaults")
if not len(defaults):
	raise Exception("Defaults file(defs/defaults.json) missing or invalid.")
for key,value in defaults.items():
	defaults[key] = types.make(value,key)

#Mutable
users = types.read("","users","user_list")
user_keys = types.read("","user_keys","user_key_list")
key_users = types.read("","key_users","key_user_list")
players = make_dict(users.keys(),"players","player")
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
