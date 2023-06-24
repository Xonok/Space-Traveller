import json,copy
from . import io,types,stats,spawner,itemdata,validation,info,config,Init
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

#Defaults
io.ensure("","world",{"ships":0})
io.ensure("","users",[])
io.ensure("","admins",[])
#Constants
lists = read("lists")
constellations = types.read("defs","constellations","dict:list:str")
constellation_of = {}
systems = {}
for name,stars in constellations.items():
	for star in stars:
		if star in constellation_of: raise Exception("Star "+star+" is in multiple constellations.")
		constellation_of[star] = name
		systems[star] = types.read("basemaps",star+"_map","system")
starmap = types.read("defs","starmap","dict:dict:str")
price_lists = make_dict("prices")
loot = make_dict("loot")
premade_ships = make_dict("premade_ships")
items = make_dict("items")
quests = make_dict("quests")
ship_types = make_dict("ship_types")
station_kits = types.read("defs","station_kits","dict:station_kit")
industries = read("industries")
machines = types.read("defs","machines","dict:machine")
gatherables = types.read("defs","gatherables","dict:gathering")
weapons = types.read("defs","weapons","dict:weapon")
objects = types.read("defs","objects","dict:object")
premade_structures = types.read("defs","premade_structures","dict:structure")
blueprints = make_dict("blueprints")
excavations = make_dict("excavations")
spawners = make_dict("spawners")
starters = read("starters")
defaults = read("defaults")
for key,value in defaults.items():
	types.current_file = "defs/defaults.json"
	defaults[key] = types.make(value,key)
for key,value in blueprints.items():
	items[key] = itemdata.blueprint(key,value,items,ship_types)
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
user_names = types.read("","users","list:str")
users = {}
for name in user_names:
	users[name] = types.read("users",name,"user")
session_to_user = {}
for key,data in users.items():
	session_to_user[data["session"]] = key
characters = {}
npc_characters = types.read("defs","npc_characters","dict:character")
for data in users.values():
	for name in data["characters"]:
		characters[name] = types.read("characters",name,"character")
for name in npc_characters.keys():
	try:
		characters[name] = types.read("characters",name,"character")
		if "ships_predefined" in characters[name]:
			del characters[name]["ships_predefined"]
		if npc_characters[name]["spawn"]:
			characters[name]["spawn"] = copy.deepcopy(npc_characters[name]["spawn"])
	except json.JSONDecodeError as e:
		raise
	except OSError as e:
		characters[name] = npc_characters[name]
ships = {}
character_ships = {}
structures = {}
for p in characters.values():
	if len(p["ships"]) == 0 and p["name"] not in npc_characters:
		raise Exception("character "+p["name"]+" is missing a ship.")
	for ship_name in p["ships"]:
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
			except Exception as e:
				print(tstruct)
				raise
		if "ships" in tile:
			for pships in tile["ships"].values():
				for ship_name in pships:
					ships[ship_name] = types.read("ships",ship_name,"ship")
for tstruct in structures.values():
	tstruct["quests"] = []
for q in quests.values():
	loc = q["start_location"]
	if loc not in structures: raise Exception("Quest "+q["name"]+" is at unknown structure: "+loc)
	structures[loc]["quests"].append(q["name"])
print("Successfully loaded defs.")

Init.run()