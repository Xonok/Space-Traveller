from . import io,items,types,user
def read(name):
	return io.read2("defs",name)
def make_dict(keys,folder,typename):
	table = {}
	for e in keys:
		table[e] = types.read(folder,e,typename)
	return table

#Constants
systems = {}
systems["Ska"] = types.read("systems","Ska","system")
items = types.read("defs","items","item_types")
quests = types.read("defs","quests","quest_types")
ship_types = types.read("defs","ship_types","ship_types")
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
	types.current_file = "defs/defaults.json"
	defaults[key] = types.make(value,key)

#Mutable
world = types.read("","world","world")
objmaps = {}
objmaps["Ska"] = types.read("objmaps","Ska","system_objects")
users = types.read("","users","dict_str")
user_keys = types.read("","user_keys","dict_str")
key_users = types.read("","key_users","dict_str")
players = make_dict(users.keys(),"players","player")
ships = {}
structures = {}
objects = {}
for p in players.values():
	pship = p["ship"]
	if pship == "":
		raise Exception("Player "+p["name"]+" is missing a ship.")
for objmap in objmaps.values():
	for tile in objmap["tiles"].get_all():
		if "structure" in tile:
			tstruct = tile["structure"]
			structures[tstruct] = types.read("structures",tstruct,"structure")
		if "object" in tile:
			tstruct = tile["object"]
			objects[tstruct] = types.read("objects",tstruct,"object")
		if "ships" in tile:
			for ship_name in tile["ships"]:
				ships[ship_name] = types.read("ships",ship_name,"ship")
for tstructure in structures.values():
	for offer in tstructure["ship_offers"]:
		ships[offer["ship"]] = types.read("ships",offer["ship"],"ship")
print("Successfully loaded defs.")
