import json
from . import io,items,types,user
def read(name):
	return io.read2("defs",name)
def make_dict(keys,folder,typename):
	table = {}
	for e in keys:
		table[e] = types.read(folder,e,typename)
	return table

#Constants
system_names = read("system_names")
systems = {}
for name in system_names:
	systems[name] = types.read("basemaps",name+"_map","system")
	print("Successfully read system "+name+" from basemaps.")
items = types.read("defs","items","item_types")
quests = types.read("defs","quests","quest_types")
ship_types = types.read("defs","ship_types","ship_types")
station_kits = types.read("defs","station_kits","station_kit_types")
planets = read("planets")
industries = read("industries")
machines = read("machines")
objects = types.read("defs","objects","dict_object")
premade_structures = types.read("defs","premade_structures","dict_structure")
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
for name in system_names:
	try:
		objmaps[name] = types.read("objmaps",name,"system_objects")
	except json.JSONDecodeError as e:
		raise
	except OSError as e:
		print(e)
		objmaps[name] = types.read("basemaps",name+"_objs","system_objects")
		print("Successfully read objmap "+name+" from basemaps.")
users = types.read("","users","dict_str")
user_keys = types.read("","user_keys","dict_str")
key_users = {}
for key,value in user_keys.items():
	key_users[value] = key
players = make_dict(users.keys(),"players","player")
ships = {}
player_ships = {}
structures = {}
for p in players.values():
	pship = p["ship"]
	if pship == "":
		raise Exception("Player "+p["name"]+" is missing a ship.")
for name,system in systems.items():
	for tile in system["tiles"].get_all():
		if "object" in tile:
			if not tile["object"] in objects:
				print("Warning: Object "+tile["object"]+" found in system "+name+" is not defined in defs/objects.json")
for name,objmap in objmaps.items():
	for tile in objmap["tiles"].get_all():
		if "structure" in tile:
			tstruct = tile["structure"]
			try:
				structures[tstruct] = types.read("structures",tstruct,"structure")
			except json.JSONDecodeError as e:
				raise
			except OSError as e:
				print(e)
				structures[tstruct] = premade_structures[tstruct]
				print("Successfully read structure "+tstruct+" from premade structures.")
		if "ships" in tile:
			for ship_name in tile["ships"]:
				ships[ship_name] = types.read("ships",ship_name,"ship")
for tstructure in structures.values():
	for offer in tstructure["ship_offers"]:
		ships[offer["ship"]] = types.read("ships",offer["ship"],"ship")
for name,data in ships.items():
	owner = data["owner"]
	if owner not in player_ships:
		player_ships[owner] = {}
	player_ships[owner][name] = name
print("Successfully loaded defs.")
