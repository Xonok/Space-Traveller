from . import items,defs,io
class Ship(dict):
	def move(self,x,y,rot):
		self["pos"]["x"] = x
		self["pos"]["y"] = y
		self["pos"]["rotation"] = rot
	def get_space(self):
		inv = self["inventory"]
		inv["space_left"] = inv["space_max"] - inv["items"].size() - inv["gear"].size()
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
	def save(self):
		io.write2("ships",self["name"],self)
def slots(name,gtype):
	if gtype not in defs.ship_types[name]["slots"]:
		return 99999
	return defs.ship_types[name]["slots"][gtype]
def slots_left(name,gtype,pgear):
	equipped = items.equipped(gtype,pgear)
	max = slots(name,gtype)
	return max-equipped
def get(ship_name):
	if not ship_name in defs.ships: return
	return defs.ships[ship_name]