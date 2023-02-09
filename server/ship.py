import copy
from . import error
class Ship(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
		self.old_name = None
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
			if "field_space_bonus" in defs.items[item]["props"]:
				inv["space_extra"] += defs.items[item]["props"]["field_space_bonus"]*amount
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
	def equip(self,data):
		on = data["ship-on"]
		off = data["ship-off"]
		pitems = self["inventory"]["items"]
		pgear = self["inventory"]["gear"]
		for item,amount in off.items():
			items.transfer(pgear,pitems,item,amount)
		for item,amount in on.items():
			items.transfer(pitems,pgear,item,amount,equip=True)
	def rename(self,new_name):
		del defs.ships[self["name"]]
		map.remove_ship(self)
		if not self.old_name:
			self.old_name = self["name"]
		self["name"] = new_name
		defs.ships[new_name] = self
		system = self["pos"]["system"]
		x = self["pos"]["x"]
		y = self["pos"]["y"]
		map.add_ship(self,system,x,y)
		self.save()
	def save(self):
		io.write2("ships",self["name"],self,self.old_name)
def slots(name,gtype):
	if gtype not in defs.ship_types[name]["slots"]:
		return 0
	return defs.ship_types[name]["slots"][gtype]
def slots_left(name,gtype,pgear):
	equipped = items.equipped(gtype,pgear)
	max = slots(name,gtype)
	return max-equipped
def prop(type_name,prop_name):
	ship_type = defs.ship_types[type_name]
	if "props" not in ship_type or prop_name not in ship_type["props"]: return
	return ship_type["props"][prop_name]
def get(ship_name):
	if ship_name not in defs.ships: return
	return defs.ships[ship_name]
def gets(player_name):
	pdata = player.data(player_name)
	pships = {}
	for ship_name in pdata["ships"]:
		pships[ship_name] = get(ship_name)
	return pships
def new(type,owner):
	if type not in defs.ship_types:
		raise Exception("Undefined ship type: "+type)
	shipdef = defs.ship_types[type]
	pship = copy.deepcopy(defs.defaults["ship"])
	id = defs.world.add_ship()
	pship["name"] = owner+","+type+","+str(id)
	pship["id"] = id
	pship["type"] = type
	pship["owner"] = owner
	pship["img"] = shipdef["img"]
	pship["inventory"]["space_max"] = shipdef["space"]
	pship["inventory"]["space_left"] = shipdef["space"]
	defs.ships[pship["name"]] = pship
	if owner not in defs.player_ships:
		defs.player_ships[owner] = {}
	defs.player_ships[owner][pship["name"]] = pship["name"]
	pship.save()
	return pship
def add_player_ship(pship):
	owner = pship["owner"]
	name = pship["name"]
	if not defs.player_ships[owner]:
		defs.player_ships[owner] = {}
	defs.player_ships[owner][name] = name
def remove_player_ship(owner,name):
	if owner not in defs.player_ships: return
	if name not in defs.player_ships[owner]: return
	del defs.player_ships[owner][name]
def enter(data,pdata):
	target_ship = get(data["ship"])
	current_ship = get(pdata["ship"])
	if not target_ship: raise error.User("There is no ship called "+data["ship"])
	if target_ship["owner"] != pdata["name"]:
		raise error.User("Can't switch to a ship owned by someone else.")
	pdata["ship"] = target_ship["name"]
	pdata.save()
def trade(self,data,pdata):
	pship = get(pdata["ship"])
	froma = data["items"]
	a = pship["inventory"]["items"]
	tship = get(data["target"])
	b = tship["inventory"]["items"]
	if not tship: raise error.User("Can't trade with a ship called "+data["target"]+" because it doesn't exist.")
	items.transaction(a,b,froma,{})
	a.save()
	b.save()
def player_ships(name):
	if name not in defs.player_ships: return {}
	table = {}
	for name in defs.player_ships[name]:
		table[name] = get(name)
	return table
def guard(data,pdata):
	dship = data["ship"]
	if len(pdata["ships"]) == 1:
		raise error.User("Can't leave your last ship behind.")
	if dship in pdata["ships"]:
		pdata["ships"].remove(dship)
		pdata.save()
def follow(data,pdata):
	dship = data["ship"]
	dshipdata = get(dship)
	if not dshipdata: raise error.User("There is no ship called "+dship)
	if dshipdata["owner"] != pdata["name"]: raise error.User("You don't own that ship.")
	first = get(pdata["ships"][0])
	fpos = first["pos"]
	dpos = dshipdata["pos"]
	xcomp = fpos["x"] == dpos["x"]
	ycomp = fpos["y"] == dpos["y"]
	scomp = fpos["system"] == dpos["system"]
	if not(xcomp and ycomp and scomp):
		raise error.User("The ship must be at the same tile.")
	if dship in pdata["ships"]: return
	pdata["ships"].append(dship)
	pdata.save()
from . import items,defs,io,map,player