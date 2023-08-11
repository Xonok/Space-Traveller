import copy,time
from . import error,tick,Item

class Ship(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
		if "props" not in self:
			self["props"] = {}
	def move(self,x,y,rot):
		map.remove_ship(self)
		system = self["pos"]["system"]
		self["pos"]["x"] = x
		self["pos"]["y"] = y
		self["pos"]["rotation"] = rot
		map.add_ship(self,system,x,y)
		self.save()
	def jump(self,target_pos):
		target_pos = copy.deepcopy(target_pos)
		map.remove_ship(self)
		map.add_ship(self,target_pos["system"],target_pos["x"],target_pos["y"])
		self["pos"] = target_pos
		self.save()
	def get_space(self):
		inv = self["inventory"]
		inv["space_max"] = defs.ship_types[self["type"]]["space"]
		inv["space_extra"] = 0
		for item,amount in inv["gear"].items():
			if "props" not in defs.items[item]: continue
			if "aura_space_bonus" in defs.items[item]["props"]:
				inv["space_extra"] += defs.items[item]["props"]["aura_space_bonus"]*amount
			if "space_max" in defs.items[item]["props"]:
				inv["space_extra"] += defs.items[item]["props"]["space_max"]*amount
		inv["space_left"] = inv["space_max"] + inv["space_extra"] - inv["items"].size() - inv["gear"].size()
		return inv["space_left"]
	def get_items(self):
		return self["inventory"]["items"]
	def get_gear(self):
		return self["inventory"]["gear"]
	def get_system(self):
		return self["pos"]["system"]
	def get_coords(self):
		return self["pos"]["x"],self["pos"]["y"]
	def trade(self,cdata,data):
		Item.transfer(cdata,data)
	def rename(self,new_name):
		if type(new_name) is not str:
			raise error.User("Ship name needs to be a string. "+str(new_name))
		if len(new_name) == 0:
			if "custom_name" in self:
				del self["custom_name"]
				self.save()
				return
		if len(new_name) < 3:
			raise error.User("Ship name can't be less than 3 letters.")
		if len(new_name) > 20:
			raise error.User("Ship name can't be more than 20 letters. You silly.")
		self["custom_name"] = new_name
		self.save()
	def tick(self):
		if "timestamp" in self:
			ticks = tick.ticks_since(self["timestamp"],"long")
			ticks = max(ticks,0)
			for i in range(ticks):
				sitems = self.get_items()
				sgear = self.get_gear()
				for item,amount in sgear.items():
					idata = defs.items[item]
					if "props" in idata and "station_mining" in idata["props"]:
						for j in range(amount):
							try:
								gathering.gather(self)
							except Exception:
								pass
				for item,amount in sgear.items():
					if item in defs.machines:
						for j in range(amount):
							factory.use_machine(item,sitems)
				self.get_space()
			ticks = tick.ticks_since(self["timestamp"],"short")
			ticks = max(ticks,0)
			for i in range(ticks):
				stats.regenerate_armor(self)
			self["timestamp"] = time.time()
		else:
			self["timestamp"] = time.time()
		
		self.save()
	def save(self):
		io.write2("ships",self["name"],self)
def prop(type_name,prop_name):
	ship_type = defs.ship_types[type_name]
	if "props" not in ship_type or prop_name not in ship_type["props"]: return
	return ship_type["props"][prop_name]
def get(ship_name):
	if ship_name not in defs.ships: return
	return defs.ships[ship_name]
def gets(character_name):
	cdata = character.data(character_name)
	pships = {}
	for ship_name in cdata["ships"]:
		pships[ship_name] = get(ship_name)
	return pships
def new(type,owner):
	if type not in defs.ship_types:
		raise Exception("Undefined ship type: "+type)
	shipdef = defs.ship_types[type]
	pship = types.copy(defs.defaults["ship"],"ship")
	id = defs.world.add_ship()
	pship["name"] = owner+","+type+","+str(id)
	pship["id"] = id
	pship["type"] = type
	pship["owner"] = owner
	pship["img"] = shipdef["img"]
	pship["inventory"]["space_max"] = shipdef["space"]
	pship["inventory"]["space_left"] = shipdef["space"]
	stats.update_ship(pship)
	defs.ships[pship["name"]] = pship
	if owner not in defs.character_ships:
		defs.character_ships[owner] = {}
	defs.character_ships[owner][pship["name"]] = pship["name"]
	pship.save()
	return pship
def add_character_ship(pship):
	owner = pship["owner"]
	name = pship["name"]
	if not defs.character_ships[owner]:
		defs.character_ships[owner] = {}
	defs.character_ships[owner][name] = name
def remove_character_ship(owner,name):
	if owner not in defs.character_ships: return
	if name not in defs.character_ships[owner]: return
	del defs.character_ships[owner][name]
def character_ships(name):
	if name not in defs.character_ships: return {}
	table = {}
	for name in defs.character_ships[name]:
		table[name] = get(name)
		table[name].tick()
	return table
def guard(data,cdata):
	dship = data["ship"]
	if len(cdata["ships"]) == 1:
		raise error.User("Can't leave your last ship behind.")
	if dship in cdata["ships"]:
		cdata["ships"].remove(dship)
		cdata.save()
def follow(data,cdata):
	dship = data["ship"]
	dshipdata = get(dship)
	if not dshipdata: raise error.User("There is no ship called "+dship)
	if dshipdata["owner"] != cdata["name"]: raise error.User("You don't own that ship.")
	first = get(cdata["ships"][0])
	fpos = first["pos"]
	dpos = dshipdata["pos"]
	xcomp = fpos["x"] == dpos["x"]
	ycomp = fpos["y"] == dpos["y"]
	scomp = fpos["system"] == dpos["system"]
	if not(xcomp and ycomp and scomp):
		raise error.User("The ship must be at the same tile.")
	if dship in cdata["ships"]: return
	cdata["ships"].append(dship)
	cdata.save()
from . import defs,io,map,character,types,factory,gathering,stats