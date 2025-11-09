import copy,time,threading

class System(dict):
	def save(self):
		io.write2("systems",self["name"],self)
class SystemObjects(dict):
	def save(self):
		io.write2("objmaps",self["name"],self)
class World(dict):
	def add_ship(self):
		self["ships"] += 1
		self.save()
		return self["ships"]
	def add_group(self):
		if "groups" not in self:
			self["groups"] = 0
		self["groups"] += 1
		self.save()
		return self["groups"]
	def save(self):
		io.write2("","world",self)
class Grid(dict):
	def __init__(self,default=None,**kwargs):
		super().__init__()
		if not default:
			default = {}
		self.default = default
		self.update(kwargs)
		self.parent = None
	def set(self,x,y,value):
		x = str(x)
		y = str(y)
		if x not in self:
			self[x] = {}
		self[x][y] = value
		if not len(value):
			del self[x][y]
		if not len(self[x]):
			del self[x]
	def get(self,x,y):
		x = str(x)
		y = str(y)
		if x not in self or y not in self[x]:
			return copy.deepcopy(self.default)
		return self[x][y]
	def get_all(self):
		list = []
		for column in self.values():
			for value in column.values():
				list.append(value)
		return list
	def save(self):
		if not self.parent: raise Exception("Parent for SaveItems not set.")
		self.parent.save()
def system(system_name):
	return defs.systems[system_name]
def tilemap(system_name):
	return defs.systems[system_name]["tiles"]
def objmap(system_name):
	return defs.objmaps[system_name]
def otiles(system_name):
	return defs.objmaps[system_name]["tiles"]
def get_otile(system_name,x,y):
	return defs.objmaps[system_name]["tiles"].get(x,y)
def wavg_spd(pships):
	w_speeds = []
	for name in pships:
		data = ship.get(name)
		speed = data["stats"]["speed"]
		weight = data["stats"]["size"]
		w_speeds.append((speed,weight))
	return func.wavg(*w_speeds)
def get_system(system_name):
	return defs.systems[system_name]
def terrain_to_resource(terrain):
	return defs.terrain[terrain]["resource"]
def get_tile(system_name,x,y):
	stiles = defs.systems[system_name]["tiles"]
	tile = copy.deepcopy(stiles.get(x,y))
	otiles = defs.objmaps[system_name]["tiles"]
	otile = otiles.get(x,y)
	if "terrain" in tile:
		tile["resource"] = terrain_to_resource(tile["terrain"])
	if "resource" in tile:
		tile["resource_amount"] = gathering.get_resource_amount(system_name,x,y)
	else:
		tile["resource_amount"] = 0
	ships = {}
	if "items" in otile:
		tile["items"] = copy.deepcopy(otile["items"])
	if "ships" in otile:
		for owner,names in otile["ships"].items():
			ship_names = copy.deepcopy(names)
			ships[owner] = []
			for name in ship_names:
				pship = ship.get(name)
				ship_type = defs.ship_types[pship["type"]]
				table = {}
				table["name"] = pship["name"]
				if "custom_name" in pship:
					table["custom_name"] = pship["custom_name"]
				table["ship"] = ship_type["name"],
				table["type"] = pship["type"]
				table["owner"] = pship["owner"]
				table["img"] = pship["img"]
				table["id"] = pship["id"]
				table["player"] = False if pship["owner"] in defs.npc_characters else True
				table["threat"] = pship["stats"]["threat"]
				table["stats"] = pship["stats"]
				ships[owner].append(table)
	if "structure" in otile:
		tile["structure"] = otile["structure"]
	if "landmark" in otile:
		tile["landmark"] = Entity.landmark.get(system_name,x,y)
	tile["ships"] = ships
	if "wormhole" in tile:
		wormhole = tile["wormhole"]
		if "target" in wormhole:
			tile["jump_target"] = wormhole["target"]["system"]
		tile["img"] = "img/wormhole.png"
		if "wormhole" in tile:
			tile["wormhole"]["img"] = defs.wormhole_types.get(tile["wormhole"]["type"],{}).get("img")
			if not tile["wormhole"]["img"]:
				tile["wormhole"]["img"] = defs.wormhole_types["Wormhole"]["img"]
	return tile
def remove_ship(pship):
	system_name = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	name = pship["name"]
	tiles = defs.objmaps[system_name]["tiles"]
	tile = tiles.get(x,y)
	if "ships" in tile and pship["owner"] in tile["ships"]:
		oships = tile["ships"][pship["owner"]]
		if name in oships:
			oships.remove(name)
		if not len(oships):
			del tile["ships"][pship["owner"]]
		if not len(tile["ships"]):
			del tile["ships"]
	tiles.set(x,y,tile)
	tiles.save()
def add_ship(pship,system_name,x,y):
	name = pship["name"]
	owner = pship["owner"]
	tiles = defs.objmaps[system_name]["tiles"]
	tile = tiles.get(x,y)
	if "ships" not in tile:
		tile["ships"] = {}
	if owner not in tile["ships"]:
		tile["ships"][owner] = []
	oships = tile["ships"][owner]
	if name not in oships:
		oships.append(name)
	pship["pos"]["system"] = system_name
	pship["pos"]["x"] = x
	pship["pos"]["y"] = y
	tiles.set(x,y,tile)
	tiles.save()
def add_ship2(pship):
	add_ship(pship,pship["pos"]["system"],pship["pos"]["x"],pship["pos"]["y"])
def get_character_ships(cdata):
	owner = cdata["name"]
	pship = ship.get(cdata.ship())
	system_name = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	otiles = defs.objmaps[system_name]["tiles"]
	otile = otiles.get(x,y)
	ships = {}
	if "ships" in otile and owner in otile["ships"]:
		for shipname in otile["ships"][owner]:			
			tship = ship.get(shipname)
			tship.tick()
			if tship["owner"] == owner:
				ships[shipname] = tship
	return ships
def get_tile_ships(system_name,x,y):
	otile = otiles(system_name).get(x,y)
	ships = []
	if "ships" not in otile:
		return ships
	for ship_names in otile["ships"].values():
		for name in ship_names:
			ships.append(ship.get(name))
	return ships
def pos_equal(a,b):
	return a["x"] == b["x"] and a["y"] == b["y"] and a["system"] == b["system"]
def get_star_data_small(star):
	result = {}
	for key,value in defs.starmap[star].items():
		if type(value) is not str: continue
		if value not in defs.systems: continue
		result[key] = value
	return result
def get_star_data(pship):
	star = pship["pos"]["system"]
	sysdata = defs.system_data[star]
	constellation = "Unknown"
	if star in defs.constellation_of:
		constellation = defs.constellation_of[star]
	result = {
		"tiles_by_terrain": {},
		"tiles": len(sysdata["tiles"]),
		"neighbours": {},
		"constellation": constellation,
		"planets": [],
		"stars": defs.starmap
	}
	
	for key,value in defs.starmap.items():
		if key not in defs.systems:
			value["no_map"] = True
	for key,value in defs.starmap[star].items():
		if type(value) is not str: continue
		if value not in defs.systems: continue
		result["neighbours"][key] = value
	for name in sysdata["tiles_by_terrain"].keys():
		result["tiles_by_terrain"][name] = len(sysdata["tiles_by_terrain"][name])
	for name,data in sysdata["planets"].items():
		entry = {}
		entry["name"] = name
		entry["consumes"] = {}
		entry["produces"] = {}
		for item in data["consumes"]:
			idata = defs.items[item]
			entry["consumes"][item] = {
				"name": idata["name"],
				"img": idata["img"]
			}
		for item in data["produces"]:
			idata = defs.items[item]
			entry["produces"][item] = {
				"name": idata["name"],
				"img": idata["img"]
			}
		result["planets"].append(entry)
	return result
	#tiles
	#neighbours
def get_owned_structures(system,name):	
	if system not in defs.system_data: raise user.Error("No system called "+system)
	table = {}
	for name2,data in defs.system_data[system]["structures_by_owner"].get(name,{}).items():
		table[name2] = {
			"name": data["name"],
			"name_custom": data.get("custom_name",""),
			"pos": data["pos"]
		}
	return table
from . import io,defs,func,structure,ship,error,gathering,Skill,Entity