import copy
from . import io,defs,func,structure,ship,error
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
			pship.move(px,py,func.direction(x,y))
def gather(tiles,x,y,pdata):
	pship = ship.get(pdata.ship())
	tile = tiles.get(x,y)
	if "terrain" in tile:
		pitems = pship.get_items()
		pgear = pship.get_gear()
		match tile["terrain"]:
			case "energy":
				pitems.add("energy",min(pship.get_space(),func.dice(3,6)))
			case "nebula":
				pitems.add("gas",min(pship.get_space(),func.dice(2,6)))
			case "asteroids":
				if pgear.get("mining_laser"):
					pitems.add("ore",min(pship.get_space(),func.dice(2,6)))
def get_system(system_name):
	return defs.systems[system_name]
def get_tiles(system,px,py,radius):
	stiles = defs.systems[system]["tiles"]
	tiles = {}
	for x in range(px-radius,px+radius+1):
		if x not in tiles:
			tiles[x] = {}
		for y in range(py-radius,py+radius+1):
			tile = copy.deepcopy(stiles.get(x,y))
			tiles[x][y] = tile
			tstructure = structure.get(system,x,y)
			if tstructure:
				tile["structure"] = copy.deepcopy(tstructure)
				tile["structure"]["image"] = defs.ship_types[tile["structure"]["ship"]]["img"]
	return tiles