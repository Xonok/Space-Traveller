class Character(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
	def init(self):
		self.get_room()
		self.get_vision()
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
			shipdef = defs.ship_types[pship["type"]]
			non_gear_room = shipdef["room"]-shipdef.get("room_gear",shipdef["room"])
			print(non_gear_room)
			current += pship["stats"]["room"]["current"]+non_gear_room
			max += shipdef["room"]
		for item,amount in self["items"].items():
			isize = Item.query.size(item)
			current -= isize*amount
		self["stats"]["room"] = {
			"current": current,
			"max": max
		}
		return self["stats"]["room"]["current"]
	def get_vision(self):
		pship = ship.get(self.ship())
		pships = ship.gets(self["name"])
		psystem,px,py = pship.loc()
		vision = 3
		tile = map.get_tile(psystem,px,py)
		ship_defs = {}
		for data in pships.values():
			ship_defs[data["type"]] = defs.ship_types[data["type"]]
			pgear = data.get_gear()
			if "highpower_scanner" in pgear:
				vision = max(vision,5)
		vision += defs.terrain[tile["terrain"]]["vision"]
		self["stats"]["vision"] = vision
		return vision
	def save(self):
		io.write2("characters",self["name"],self)

import time
from . import io,defs,error,ship,Item,map

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