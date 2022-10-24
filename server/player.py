class Player(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
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
		io.write2("players",self["name"],self)

from . import io,items,defs

def data(name):
	if not name in defs.players:
		raise Exception("No player called "+name+".")
	return defs.players[name]