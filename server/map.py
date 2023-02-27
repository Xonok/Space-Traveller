import copy,time

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
def tilemap(system):
	return defs.systems[system]["tiles"]
def objmap(system):
	return defs.objmaps[system]["tiles"]
def move(data,cdata):
	pship = ship.get(cdata.ship())
	psystem = pship.get_system()
	prev_x,prev_y = pship.get_coords()
	px,py = data["position"]
	if not pathable(psystem,px,py):
		raise error.User("Can't move there.")
	x = px-prev_x
	y = prev_y-py
	if x != 0 or y != 0:
		pships = cdata["ships"]
		if pship["name"] in pships:
			for s in pships:
				ship.get(s).move(px,py,func.direction(x,y))
		else:
			pship.move(px,py,func.direction(x,y))
def move2(data,cdata):
	pship = ship.get(cdata.ship())
	pships = cdata["ships"]
	psystem = pship.get_system()
	tx,ty = data["position"]
	if not pathable(psystem,tx,ty): raise error.User("Can't move there.")
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	if tx == x and ty == y:
		return
	final_move_x = 0
	final_move_y = 0
	dx = tx-x
	dy = ty-y
	prev_x = x
	prev_y = y
	path = []
	path.append((x,y))
	while dx != 0 or dy != 0:
		prev_x = x
		prev_y = y
		x_off = 0
		y_off = 0
		if dx > 0: x_off = 1
		if dx < 0: x_off = -1
		if dy > 0: y_off = 1
		if dy < 0: y_off = -1
		if pathable(psystem,x+x_off,y+y_off):
			pass
		elif x_off and pathable(psystem,x+x_off,y):
			y_off = 0
		elif x_off and pathable(psystem,x+x_off,y+1):
			y_off = 1
		elif x_off and pathable(psystem,x+x_off,y-1):
			y_off = -1
		elif y_off and pathable(psystem,x,y+y_off):
			x_off = 0
		elif y_off and pathable(psystem,x+1,y+y_off):
			x_off = 1
		elif y_off and pathable(psystem,x-1,y+y_off):
			x_off = -1
		else:
			break
		x += x_off
		y += y_off
		if (x,y) in path:
			break
		path.append((x,y))
		dx = tx-x
		dy = ty-y
	if x == pship["pos"]["x"] and y == pship["pos"]["y"]:
		raise error.User("Can't find a path there.")
	last = path[-1]
	pre_last = path[-2]
	final_move_x = last[0]-pre_last[0]
	final_move_y = last[1]-pre_last[1]
	if pship["name"] in pships:
		for s in pships:
			ship.get(s).move(x,y,func.direction(final_move_x,final_move_y))
	else:
		pship.move(x,y,func.direction(final_move_x,final_move_y))
	return path
def pathable(system_name,x,y):
	return "terrain" in tilemap(system_name).get(x,y)
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
def get_tile(system,x,y,username):
	stiles = defs.systems[system]["tiles"]
	tile = copy.deepcopy(stiles.get(x,y))
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
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
		tile["resource_amount"] = gathering.get_resource_amount(otiles,x,y)
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
				#if pship["owner"] != username:
				table = {}
				table["name"] = pship["name"]
				if "custom_name" in pship:
					table["custom_name"] = pship["custom_name"]
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
def add_ship2(pship):
	add_ship(pship,pship["pos"]["system"],pship["pos"]["x"],pship["pos"]["y"])
def get_character_ships(cdata):
	owner = cdata["name"]
	pship = ship.get(cdata.ship())
	system = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
	ships = {}
	if "ships" in otile and owner in otile["ships"]:
		for shipname in otile["ships"][owner]:			
			tship = ship.get(shipname)
			tship.tick()
			if tship["owner"] == owner:
				ships[shipname] = tship
	return ships
def get_tile_ships(system,x,y):
	otiles = objmap(system)
	otile = otiles.get(x,y)
	ships = []
	if "ships" not in otile:
		return ships
	for ship_names in otile["ships"].values():
		for name in ship_names:
			ships.append(ship.get(name))
	return ships
def jump(self,data,cdata):
	object_name = data["wormhole"]
	if object_name not in defs.objects: raise error.User("This object doesn't have a definition yet.")
	wormhole = defs.objects[object_name]
	if "target" not in wormhole: raise error.User("This wormhole isn't open.")
	target = wormhole["target"]
	for s in cdata["ships"]:
		pship = ship.get(s)
		pship.jump(target)
def pos_equal(a,b):
	return a["x"] == b["x"] and a["y"] == b["y"] and a["system"] == b["system"]
from . import io,defs,func,structure,ship,error,gathering