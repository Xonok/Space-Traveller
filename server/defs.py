import json,copy,hashlib
from . import io,types,itemdata,info,exploration,tick,Item
def read_def(*path):
	return io.read2(["defs",*path])
def read_mutable(*path):
	return io.read2(["data",*path])
def make_dict_def(folder):
	global lists
	table = {}
	data = lists[folder]
	for fname in data["files"]:
		if fname == "*":
			types.read_defs(table,data["type"],folder)
		else:
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
		if fname == "*":
			types.reads(table,data["type"],folder)
		else:
			table[fname] = types.read(data["type"],folder,fname)
		#table[fname] = types.read(data["type"],folder,fname)
	if data["merge"]:
		table2 = {}
		for folder,files in table.items():
			for name,fdata in files.items():
				table2[name] = fdata
		table = table2
	return table

print("Begin loading defs.")
#Defaults
io.ensure("world",{"ships":0,"flip_done":True})
io.ensure("users",[])
io.ensure("admins",[])
#Constants
print("...constants")
lists = read_def("defs","lists")
constellations = types.read_def("dict:list:str","defs","constellations")
constellation_of = {}
systems = make_dict_def("basemaps")
for name,stars in constellations.items():
	for star in stars:
		if star in constellation_of: raise Exception("Star "+star+" is in multiple constellations.")
		constellation_of[star] = name
starmap = make_dict_def("starmap")
price_lists = make_dict_def("prices")
loot = make_dict_def("loot")
lore = make_dict_def("lore")
predefined_ships = make_dict_def("predefined_ships")
items = make_dict_def("items")
name_to_iname = {}
quests = make_dict_def("quests")
ship_types = make_dict_def("ship_types")
station_kits = types.read_def("dict:station_kit","defs","station_kits")
industries2 = make_dict_def("industries")
machines = types.read_def("dict:machine","defs","machines")
wormhole_types = types.read_def("dict:wormhole_def","defs","wormhole_types")
factions = types.read_def("dict:faction_def","defs","factions")
gatherables = types.read_def("dict:gathering","defs","gatherables")
weapons = types.read_def("dict:weapon","defs","weapons")
objects = types.read_def("dict:object","defs","objects")
predefined_structures = types.read_def("dict:structure_predef","defs","predefined_structures")
blueprints = make_dict_def("blueprints")
excavation_locations = types.read_def("dict:excavation_location","defs","excavation_locations")
spawners = make_dict_def("spawners")
pops = read_def("defs","pops")
terrain = read_def("defs","terrain")
assigned_industries = read_def("defs","assigned_industries")
item_categories = read_def("defs","item_categories")
skills = make_dict_def("skills")
skill_locations = types.read_def("dict:dict:skill_loc_entry","defs","skill_locations")
starters = read_def("defs","starters")
defaults = read_def("defs","defaults")
npc_characters = types.read_def("dict:character","defs","npc_characters")
for key,value in defaults.items():
	types.current_file = "defs/defaults.json"
	defaults[key] = types.make(value,key)
for name,data in items.items():
	if data["name"] in name_to_iname:
		print("Duplicate item name in item("+name+"): "+data["name"])
	name_to_iname[data["name"]] = name
	if "name_pluto" in data:
		if data["name_pluto"] in name_to_iname:
			print("Duplicate item name in item("+name+"): "+data["name_pluto"])
		name_to_iname[data["name_pluto"]] = name

#Mutable
print("...mutable.")
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
users_lowercase = {}
for name in user_names:
	users[name] = types.read("user","users",name)
	users_lowercase[name.lower()] = users[name]
session_to_user = {}
for key,data in users.items():
	session_to_user[data["session"]] = key
characters = {}
characters_lowercase = {}
achievements = {}
for data in users.values():
	for name in data["characters"]:
		characters[name] = types.read("character","characters",name)
		characters_lowercase[name.lower()] = characters[name]
		try:
			if name not in npc_characters:
				achievements[name] = types.read("achievements","achievements",name)
		except json.JSONDecodeError:
			raise
		except OSError:
			achievements[name] = types.make(exploration.default_params(name),"achievements")
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
ships = make_dict("ships")
character_ships = {}
tag_to_ship = {}
structures = {}
character_structures = {}
for p in characters.values():
	if len(p["ships"]) == 0 and p["name"] not in npc_characters:
		raise Exception("character "+p["name"]+" is missing a ship.")
	# for ship_name in p["ships"]:
		# ships[ship_name] = types.read("ship","ships",ship_name)
for name,objmap in objmaps.items():
	# for tile in objmap["tiles"].get_all():
	for x,col in objmap["tiles"].items():
		for y,otile in col.items():
			btiles = systems[name]["tiles"]
			btile = btiles.get(x,y)
			
			struct_name = otile.get("structure",btile.get("structure"))
			if struct_name:
				try:
					structures[struct_name] = types.read("structure","structures",struct_name)
					if "demands" in structures[struct_name]["market"]:
						del structures[struct_name]["market"]["demands"]
				except json.JSONDecodeError as e:
					raise
				except OSError as e:
					# print(e)
					#structures[struct_name] = copy.deepcopy(predefined_structures[struct_name])
					predef = copy.deepcopy(predefined_structures[struct_name])
					if "level" in predef:
						del predef["level"]
					structures[struct_name] = types.copy(defaults["structure"]|predef,"structure")
					del structures[struct_name]["market"]["lists"]
					del structures[struct_name]["market"]["demands"]
					otile["structure"] = struct_name
					objmap["tiles"].set(x,y,otile)
					objmap["tiles"].save()
					print("Successfully read structure "+struct_name+" from predefined structures.")
				except Exception as e:
					print(struct_name)
					raise
			# if "ships" in otile:
				# for pships in otile["ships"].values():
					# for ship_name in pships:
						# ships[ship_name] = types.read("ship","ships",ship_name)
for struct_name in predefined_structures.keys():
	if struct_name not in structures:
		predef = copy.deepcopy(predefined_structures[struct_name])
		if "level" in predef:
			del predef["level"]
		structures[struct_name] = types.copy(defaults["structure"]|predef,"structure")
		otiles = objmaps[predef["pos"]["system"]]["tiles"]
		px = predef["pos"]["x"]
		py = predef["pos"]["y"]
		otile = otiles.get(px,py)
		otile["structure"] = struct_name
		otiles.set(px,py,otile)
		otiles.save()
for tstruct in structures.values():
	tstruct["quests"] = []
groups = make_dict("groups")
group_of = {}
for id,group in groups.items():
	for name in group["members"]:
		group_of[name] = group
for q in quests.values():
	loc = q["start_location"]
	if loc not in structures: raise Exception("Quest "+q["name"]+" is at unknown structure: "+loc)
	structures[loc]["quests"].append(q["name"])
print("Successfully loaded defs.")

#generated info
print("Generating system data.")
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
		"tiles": [],
		"structures_by_owner": {},
		"wormholes": {},
		"planets": {}
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
			wormhole = data.get("wormhole")
			structure = data.get("structure")
			if wormhole:
				wh_name = name+",WH,"+str(x)+","+str(y)
				wormhole["x"] = int(x)
				wormhole["y"] = int(y)
				sysdata["wormholes"][wh_name] = wormhole
			if structure:
				planet = {
					"consumes": [],
					"produces": []
				}
				sysdata["planets"][structure] = planet
				assigned = assigned_industries.get(structure)
				if assigned:
					for ind in assigned:
						ind_def = industries2[ind]
						for item in ind_def["input"].keys():
							if item not in planet["consumes"]:
								planet["consumes"].append(item)
						for item in ind_def["output"].keys():
							if item not in planet["produces"]:
								planet["produces"].append(item)
	objmap = objmaps[name]
	otiles = objmap["tiles"]
	for x,col in otiles.items():
		for y,data in col.items():
			if "structure" in data:
				if data["structure"] not in structures:
					raise Exception("Unknown structure: "+data["structure"])
				sdata = structures[data["structure"]]
				owner = sdata["owner"]
				if owner not in sysdata["structures_by_owner"]:
					sysdata["structures_by_owner"][owner] = {}
				sysdata["structures_by_owner"][owner][sdata["name"]] = sdata
from . import Init
print("Initializing.")
Init.run()
print("Finished initializing.")
print("Calculating data hashes.")
def get_full_idata():
	data = items | ship_types
	for name in list(data.keys()):
		if name in items:
			idata = items[name]
			props = idata.get("props",{})
			itype = Item.query.type(name)
			category_usable = "use" in item_categories.get(itype)
			usable = True if itype == "factory" or "consumable" in props else False
		if name in ship_types:
			category_usable = True
			data[name]["type"] = "ship"
		data[name]["usable"] = category_usable or usable
	return data
full_idata = get_full_idata()
idata_hash = hashlib.sha256(json.dumps(full_idata).encode()).hexdigest()
tick.init()
print("Saving now enabled.")
info.display()