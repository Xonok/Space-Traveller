import copy,time
from . import io,defs,func,structure,ship,error

#in seconds
time_per_tick = 60*60 # 1 hour per tick.

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
	def save(self):
		io.write2("","world",self)
class Grid(dict):
	def __init__(self,default={},**kwargs):
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
def move(self,data,pdata):
	self.check(data,"position")
	pship = ship.get(pdata.ship())
	psystem = pship.get_system()
	stiles = defs.systems[psystem]["tiles"]
	prev_x,prev_y = pship.get_coords()
	px,py = data["position"]
	tile = stiles.get(px,py)
	if "terrain" not in tile:
		raise error.User("Can't move there.")
	else:
		x = px-prev_x
		y = prev_y-py
		if x != 0 or y != 0:
			ships = pdata["ships"]
			if pship["name"] in ships:
				for s in ships:
					s.move(px,py,func.direction(x,y))
			else:
				pship.move(px,py,func.direction(x,y))
def reduce_resource(system,x,y,amount):
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
	current = get_resource_amount(system,x,y)
	otile["resource_amount"] = current-amount
	if "timestamp" not in otile:
		otile["timestamp"] = time.time()
	otiles.set(x,y,otile)
	otiles.save()
def gather(tiles,x,y,pdata):
	pship = ship.get(pdata.ship())
	system = pship["pos"]["system"]
	tile = tiles.get(x,y)
	if "terrain" in tile:
		pitems = pship.get_items()
		pgear = pship.get_gear()
		amount = get_resource_amount(system,x,y)
		match tile["terrain"]:
			case "energy":
				roll = func.dice(3,6)
				if pgear.get("mining_organ"): roll += 1
				amount = min(pship.get_space(),roll,amount)
				pitems.add("energy",amount)
				reduce_resource(system,x,y,amount)
			case "nebula":
				roll = func.dice(2,6)
				if pgear.get("mining_organ"): roll += 1
				amount = min(pship.get_space(),roll,amount)
				pitems.add("gas",amount)
				reduce_resource(system,x,y,amount)
			case "asteroids":
				if pgear.get("mining_laser") or pgear.get("cutting_laser") or pgear.get("mining_organ"):
					roll = func.dice(2,6)
					if pgear.get("mining_organ"): roll += 1
					amount = min(pship.get_space(),roll,amount)
					pitems.add("ore",amount)
					if amount > 0 and pgear.get("cutting_laser"):
						if func.dice(1,10) == 10:
							pitems.add("gems",min(1,pship.get_space()))
					reduce_resource(system,x,y,amount)
			case "exotic":
				roll = func.dice(1,6)
				if pgear.get("mining_organ"): roll += 1
				amount = min(pship.get_space(),roll,amount)
				pitems.add("exotic_matter",amount)
				reduce_resource(system,x,y,amount)
			case "phase":
				roll = func.dice(1,4)-1
				if pgear.get("mining_organ"): roll += 1
				amount = min(pship.get_space(),roll,amount)
				pitems.add("phase_vapor",amount)
				reduce_resource(system,x,y,amount)
def get_system(system_name):
	return defs.systems[system_name]
def get_tiles(system,px,py,radius):
	stiles = defs.systems[system]["tiles"]
	otiles = defs.objmaps[system]["tiles"]
	tiles = {}
	for x in range(px-radius,px+radius+1):
		if x not in tiles:
			tiles[x] = {}
		for y in range(py-radius,py+radius+1):
			tile = copy.deepcopy(stiles.get(x,y))
			otile = otiles.get(x,y)
			tiles[x][y] = tile
			if "ships" in otile:
				for owner,ship_names in otile["ships"].items():
					if len(ship_names):
						pship = ship.get(ship_names[0])
						table = {}
						table["type"] = pship["type"]
						table["img"] = pship["img"]
						table["rotation"] = pship["pos"]["rotation"]
						tile["ship"] = table
			tstructure = structure.get(system,x,y)
			if tstructure:
				tile["structure"] = copy.deepcopy(tstructure)
				tile["structure"]["image"] = defs.ship_types[tile["structure"]["ship"]]["img"]
			if "object" in tile:
				tile["img"] = "img/wormhole.png"
	return tiles
def get_resource_amount(system,x,y):
	stiles = defs.systems[system]["tiles"]
	tile = stiles.get(x,y)
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
	if tile["terrain"] == "space": return 0
	if "resource_amount" not in otile: return 500
	now = time.time()
	while otile["timestamp"]+time_per_tick < now:
		otile["timestamp"] += time_per_tick
		otile["resource_amount"] += 10
		if otile["resource_amount"] >= 500:
			del otile["timestamp"]
			del otile["resource_amount"]
			break
	otiles.set(x,y,otile)
	otiles.save()
	if "resource_amount" not in otile: return 500
	return otile["resource_amount"]
def get_tile(system,x,y,username):
	stiles = defs.systems[system]["tiles"]
	tile = copy.deepcopy(stiles.get(x,y))
	resources = {
		"space": None,
		"energy": "energy",
		"nebula": "gas",
		"asteroids": "ore",
		"exotic": "exotic_matter",
		"phase": "phase_vapor"
	}
	tile["resource"] = resources[tile["terrain"]]
	if tile["resource"]:
		tile["resource_amount"] = get_resource_amount(system,x,y)
	else:
		tile["resource_amount"] = 0
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
	ships = {}
	if "ships" in otile:
		for owner,names in otile["ships"].items():
			ship_names = copy.deepcopy(names)
			ships[owner] = []
			for name in ship_names:
				pship = ship.get(name)
				if pship["owner"] != username:
					table = {}
					table["name"] = pship["name"]
					table["type"] = pship["type"]
					table["owner"] = pship["owner"]
					table["img"] = pship["img"]
					ships[owner].append(table)
	tile["ships"] = ships
	if "object" in tile:
		if tile["object"] in defs.objects:
			wormhole = defs.objects[tile["object"]]
			if "target" in wormhole:
				tile["jump_target"] = wormhole["target"]["system"]
		tile["img"] = "img/wormhole.png"
	return tile
def remove_ship(pship):
	system = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	name = pship["name"]
	tiles = defs.objmaps[system]["tiles"]
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
def add_ship(pship,system,x,y):
	name = pship["name"]
	owner = pship["owner"]
	tiles = defs.objmaps[system]["tiles"]
	tile = tiles.get(x,y)
	if "ships" not in tile:
		tile["ships"] = {}
	if owner not in tile["ships"]:
		tile["ships"][owner] = []
	oships = tile["ships"][owner]
	if name not in oships:
		oships.append(name)
	tiles.set(x,y,tile)
	tiles.save()
def get_player_ships(pdata):
	owner = pdata["name"]
	pship = ship.get(pdata["ship"])
	system = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
	ships = {}
	if "ships" in otile:
		for shipname in otile["ships"]:
			tship = ship.get(shipname)
			if tship["owner"] == owner:
				ships[shipname] = tship
	return ships
def jump(self,data,pdata):
	object_name = data["wormhole"]
	if object_name not in defs.objects: raise error.User("This object doesn't have a definition yet.")
	wormhole = defs.objects[object_name]
	if "target" not in wormhole: raise error.User("This wormhole isn't open.")
	target = copy.deepcopy(wormhole["target"])
	pship = ship.get(pdata.ship())
	remove_ship(pship)
	add_ship(pship,target["system"],target["x"],target["y"])
	pship["pos"] = target
	pship.save()