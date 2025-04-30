class Character(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
	def init(self):
		self.get_room()
	def ship(self):
		if self["ship"] not in self["ships"]:
			self["ship"] = ""
		if self["ship"]: return self["ship"]
		self["ship"] = self["ships"][0]
		return self["ships"][0]
	def get_items(self):
		return self["items"]
	def get_room(self):
		current = 0
		max = 0
		for name in self["ships"]:
			pship = ship.get(name)
			pship.get_room()
			current += pship["stats"]["room"]["current"]
			max += pship["stats"]["room"]["max"]
		for item,amount in self["items"].items():
			isize = Item.query.size(item)
			current -= isize*amount
		self["stats"]["room"] = {
			"current": current,
			"max": max
		}
		return self["stats"]["room"]["current"]
	def save(self):
		io.write2("characters",self["name"],self)

import time
from . import io,defs,error,ship,Item

def data(name):
	if not name in defs.characters:
		raise Exception("No character called "+name+".")
	return defs.characters[name]
def remove_ship(pship):
	cdata = data(pship["owner"])
	name = pship["name"]
	if name in cdata["ships"]:
		cdata["ships"].remove(name)
	if cdata["ship"] == name:
		cdata["ship"] = ""
		if len(cdata["ships"]):
			cdata["ship"] = cdata["ships"][0]
def give_credits(cdata,target,amount):
	tdata = defs.characters.get(target)
	if not tdata: raise error.User("There is no character called "+target)
	if target in defs.npc_characters: raise error.User("Can't give credits to NPCs.")
	if cdata["credits"] < amount: raise error.User("Not enough credits.")
	cdata["credits"] -= amount
	tdata["credits"] += amount
	cdata.save()
	tdata.save()
def update_active(cdata):
	if "props" not in cdata:
		cdata["props"] = {}
	cdata["props"]["last_active"] = time.time()
	cdata.save()