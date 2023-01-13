import json,copy
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
price_list_names = read("price_lists")
systems = {}
price_lists = {}
for name in system_names:
	systems[name] = types.read("basemaps",name+"_map","system")
for name in price_list_names:
	price_lists[name] = types.read("prices",name,"price_setup")
constellations = types.read("defs","constellations","dict_constellation")
constellation_of = {}
for name,stars in constellations.items():
	for star in stars:
		if star in constellation_of: raise Exception("Star "+star+" is in multiple constellations.")
		constellation_of[star] = name
item_defs = types.read("defs","items","list_str")
items = {}
for list_name in item_defs:
	items = items | types.read("items",list_name,"item_types")
quests = types.read("defs","quests","quest_types")
ship_types = types.read("defs","ship_types","ship_types")
station_kits = types.read("defs","station_kits","station_kit_types")
planets = read("planets")
industries = read("industries")
machines = read("machines")
weapons = types.read("defs","weapons","dict_weapon")
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
		# print(e)
		objmaps[name] = types.read("basemaps",name+"_objs","system_objects")
		print("Successfully read objmap "+name+" from basemaps.")
users = types.read("","users","dict_str")
user_keys = types.read("","user_keys","dict_str")
key_users = {}
for key,value in user_keys.items():
	key_users[value] = key
players = make_dict(users.keys(),"players","player")
npc_players = types.read("defs","npc_players","dict_player")
ships = {}
player_ships = {}
structures = {}
for p in players.values():
	pships = p["ships"]
	if len(pships) == 0:
		raise Exception("Player "+p["name"]+" is missing a ship.")
	for ship_name in pships.keys():
		ships[ship_name] = types.read("ships",ship_name,"ship")
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
				# print(e)
				structures[tstruct] = copy.deepcopy(premade_structures[tstruct])
				del structures[tstruct]["market"]["lists"]
				del structures[tstruct]["population"]["industries"]
				print("Successfully read structure "+tstruct+" from premade structures.")
		if "ships" in tile:
			for pships in tile["ships"].values():
				for ship_name in pships:
					ships[ship_name] = types.read("ships",ship_name,"ship")
for name,data in ships.items():
	owner = data["owner"]
	if owner not in player_ships:
		player_ships[owner] = {}
	player_ships[owner][name] = name
print("Successfully loaded defs.")
