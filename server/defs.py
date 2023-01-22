import json,copy
from . import io,items,types,user
def read(name):
	return io.read2("defs",name)
def make_dict(folder):
	global lists
	table = {}
	data = lists[folder]
	for fname in data["files"]:
		table[fname] = types.read(folder,fname,data["type"])
	if data["merge"]:
		table2 = {}
		for folder,files in table.items():
			for name,fdata in files.items():
				table2[name] = fdata
		table = table2
	return table

#Constants
lists = read("lists")
constellations = types.read("defs","constellations","dict_constellation")
constellation_of = {}
systems = {}
for name,stars in constellations.items():
	for star in stars:
		if star in constellation_of: raise Exception("Star "+star+" is in multiple constellations.")
		constellation_of[star] = name
		systems[star] = types.read("basemaps",star+"_map","system")
price_lists = make_dict("prices")
loot = make_dict("loot")
premade_ships = make_dict("premade_ships")
items = make_dict("items")
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
defaults = read("defaults")
for key,value in defaults.items():
	types.current_file = "defs/defaults.json"
	defaults[key] = types.make(value,key)

#Mutable
world = types.read("","world","world")
objmaps = {}
for name in systems.keys():
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
players = {}
npc_players = types.read("defs","npc_players","dict_player")
for name in users.keys():
	players[name] = types.read("players",name,"player")
for name in npc_players.keys():
	try:
		players[name] = types.read("players",name,"player")
		if "ships_predefined" in players[name]:
			del players[name]["ships_predefined"]
	except json.JSONDecodeError as e:
		raise
	except OSError as e:
		players[name] = npc_players[name]
ships = {}
player_ships = {}
structures = {}
for p in players.values():
	if len(p["ships"]) == 0 and p["name"] not in npc_players:
		raise Exception("Player "+p["name"]+" is missing a ship.")
	for ship_name in p["ships"].keys():
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
				if "demands" in structures[tstruct]["market"]:
					del structures[tstruct]["market"]["demands"]
			except json.JSONDecodeError as e:
				raise
			except OSError as e:
				# print(e)
				structures[tstruct] = copy.deepcopy(premade_structures[tstruct])
				del structures[tstruct]["market"]["lists"]
				del structures[tstruct]["market"]["demands"]
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
