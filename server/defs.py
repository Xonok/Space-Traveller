import json,copy
from . import io,types,itemdata,Init
def read_def(*path):
	return io.read2(["defs",*path])
def read_mutable(*path):
	return io.read2(["data",*path])
def make_dict_def(folder):
	global lists
	table = {}
	data = lists[folder]
	for fname in data["files"]:
		table[fname] = types.read_def(data["type"],folder,fname)
	if data["merge"]:
		table2 = {}
		for folder,files in table.items():
			for name,fdata in files.items():
				table2[name] = fdata
		table = table2
	return table
def make_dict(folder):
	global lists
	table = {}
	data = lists[folder]
	for fname in data["files"]:
		table[fname] = types.read(data["type"],folder,fname)
	if data["merge"]:
		table2 = {}
		for folder,files in table.items():
			for name,fdata in files.items():
				table2[name] = fdata
		table = table2
	return table

#Defaults
io.ensure("world",{"ships":0,"flip_done":True})
io.ensure("users",[])
io.ensure("admins",[])
#Constants
lists = read_def("defs","lists")
constellations = types.read_def("dict:list:str","defs","constellations")
constellation_of = {}
systems = {}
for name,stars in constellations.items():
	for star in stars:
		if star in constellation_of: raise Exception("Star "+star+" is in multiple constellations.")
		constellation_of[star] = name
		systems[star] = types.read_def("system","basemaps",star)
starmap = types.read_def("dict:dict:str","defs","starmap")
price_lists = make_dict_def("prices")
loot = make_dict_def("loot")
lore = make_dict_def("lore")
premade_ships = make_dict_def("premade_ships")
items = make_dict_def("items")
quests = make_dict_def("quests")
ship_types = make_dict_def("ship_types")
station_kits = types.read_def("dict:station_kit","defs","station_kits")
industries2 = make_dict_def("industries")
machines = types.read_def("dict:machine","defs","machines")
gatherables = types.read_def("dict:gathering","defs","gatherables")
weapons = types.read_def("dict:weapon","defs","weapons")
objects = types.read_def("dict:object","defs","objects")
predefined_structures = types.read_def("dict:structure_predef","defs","predefined_structures")
blueprints = make_dict_def("blueprints")
excavations = make_dict_def("excavations")
spawners = make_dict_def("spawners")
pops = read_def("defs","pops")
terrain = read_def("defs","terrain")
assigned_industries = read_def("defs","assigned_industries")
item_categories = read_def("defs","item_categories")
starters = read_def("defs","starters")
defaults = read_def("defs","defaults")
npc_characters = types.read_def("dict:character","defs","npc_characters")
for key,value in defaults.items():
	types.current_file = "defs/defaults.json"
	defaults[key] = types.make(value,key)
for key,value in blueprints.items():
	items[key] = itemdata.blueprint(key,value,items,ship_types)
#Mutable
world = types.read("world","world")
objmaps = {}
for name in systems.keys():
	try:
		objmaps[name] = types.read("system_objects","objmaps",name)
	except json.JSONDecodeError as e:
		raise
	except OSError as e:
		# print(e)
		objmaps[name] = types.read_def("dict","basemaps",name)
		def ifdel(table,key):
			if key in table:
				del table[key]
		ifdel(objmaps[name],"props")
		for x,col in dict(objmaps[name]["tiles"].items()).items():
			for y,tile in dict(col.items()).items():
				ifdel(tile,"terrain")
				ifdel(tile,"variation")
				ifdel(tile,"wormhole")
				if not len(tile): del col[y]
			if not len(col):
				del objmaps[name]["tiles"][x]
		objmaps[name] = types.make(objmaps[name],"system_objects")
		print("Successfully read objmap "+name+" from basemaps.")
user_names = types.read("list:str","users")
users = {}
for name in user_names:
	users[name] = types.read("user","users",name)
session_to_user = {}
for key,data in users.items():
	session_to_user[data["session"]] = key
characters = {}
for data in users.values():
	for name in data["characters"]:
		characters[name] = types.read("character","characters",name)
for name in npc_characters.keys():
	try:
		characters[name] = types.read("character","characters",name)
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
		ships[ship_name] = types.read("ship","ships",ship_name)
for name,objmap in objmaps.items():
	for tile in objmap["tiles"].get_all():
		if "structure" in tile:
			tstruct = tile["structure"]
			try:
				structures[tstruct] = types.read("structure","structures",tstruct)
				if "demands" in structures[tstruct]["market"]:
					del structures[tstruct]["market"]["demands"]
			except json.JSONDecodeError as e:
				raise
			except OSError as e:
				# print(e)
				#structures[tstruct] = copy.deepcopy(predefined_structures[tstruct])
				structures[tstruct] = types.copy(defaults["structure"]|copy.deepcopy(predefined_structures[tstruct]),"structure")
				del structures[tstruct]["market"]["lists"]
				del structures[tstruct]["market"]["demands"]
				print("Successfully read structure "+tstruct+" from predefined structures.")
			except Exception as e:
				print(tstruct)
				raise
		if "ships" in tile:
			for pships in tile["ships"].values():
				for ship_name in pships:
					ships[ship_name] = types.read("ship","ships",ship_name)
for tstruct in structures.values():
	tstruct["quests"] = []
for q in quests.values():
	loc = q["start_location"]
	if loc not in structures: raise Exception("Quest "+q["name"]+" is at unknown structure: "+loc)
	structures[loc]["quests"].append(q["name"])
print("Successfully loaded defs.")

def flip_map(table):
	new = {
		"name": table["name"]
	}
	if "props" in table:
		new["props"] = table["props"]
	new_tiles = {}
	for x,column in table["tiles"].items():
		new_tiles[x] = {}
		for y, data in column.items():
			if "object" in data:
				data["wormhole"] = objects[data["object"]]
				if "target" in data["wormhole"]:
					data["wormhole"]["target"]["y"] = -data["wormhole"]["target"]["y"]
				del data["object"]
			if "structure" in data:
				name_old = data["structure"]
				name_new = data["structure"]
				tstruct = structures.get(name_old)
				if name_old not in predefined_structures:
					system = tstruct["pos"]["system"]
					px = tstruct["pos"]["x"]
					py = str(-int(y))
					name_new = system+","+str(px)+","+str(py)
					print(name_old,name_new)
				if name_old in structures:
					del structures[name_old]
					tstruct["pos"]["y"] = -tstruct["pos"]["y"]
					structures[name_new] = tstruct
					if name_old != name_new:
						print(name_old,name_new)
						#save while deleting previous
						io.write2("structures",name_new,tstruct,name_old)
					tstruct.save()
				data["structure"] = name_new
			new_tiles[x][str(-int(y))] = data
			if "ships" in data:
				for ship_names in data["ships"].values():
					for ship_name in ship_names:
						pship = ships[ship_name]
						pship["pos"]["y"] = -pship["pos"]["y"]
						pship.save()
	new["tiles"] = new_tiles
	return new
if not world.get("flip_done"):
	for name,data in systems.items():
		systems[name] = types.make(flip_map(data),"system")
		io.write2("basemaps",name,systems[name])
	for name,data in objmaps.items():
		objmaps[name] = types.make(flip_map(data),"system_objects")
		objmaps[name].save()
	#NOTE: basemaps are in repo, so shouldn't be updated anymore.
	#base objmaps not in memory, but need to update them too
	#for name,stars in constellations.items():
	#	for star in stars:
	#		base_objmap = types.read("basemaps",star,"dict")
	#		base_objmap = types.make(flip_map(base_objmap),"system")
	#		io.write2("basemaps",star,base_objmap)
	#spawners, updated separately due to difficulties with saving them.
	for name,data in spawners.items():
		pass
	world["flip_done"] = True
	world.save()

#generated info

system_data = {}
for name,data in systems.items():
	system_data[name] = {
		"tiles_by_terrain": {
			"space": [],
			"energy": [],
			"nebula": [],
			"asteroids": [],
			"exotic": [],
			"phase": []
		},
		"tiles": []
	}
	sysdata = system_data[name]
	tiles = data["tiles"]
	for x,col in tiles.items():
		for y,data in col.items():
			tiledata = copy.deepcopy(data)
			tiledata["system"] = name
			tiledata["x"] = x
			tiledata["y"] = y
			sysdata["tiles_by_terrain"][data["terrain"]].append(tiledata)
			sysdata["tiles"].append(tiledata)

Init.run()
io.init()