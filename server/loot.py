import random
from . import defs,map,error,items,ship
def drop(target):
	if "loot" not in target: return
	loot_table = defs.loot[target["loot"]]
	pos = target["pos"]
	objmap = map.objmap(pos["system"])
	objtile = objmap.get(pos["x"],pos["y"])
	if "items" not in objtile:
		objtile["items"] = {}
	for data in loot_table["rolls"]:
		if random.randint(1,data["rarity"]) == 1:
			item = data["item"]
			if item not in objtile["items"]:
				objtile["items"][item] = 0
			objtile["items"][item] += random.randint(data["min"],data["max"])
	objmap.set(pos["x"],pos["y"],objtile)
	objmap.save()
def take(data,pdata):
	pship = ship.get(data["ship"])
	if pship["owner"] != pdata["name"]: raise error.User("You don't own the ship: "+pship["name"])
	titems = data["items"]
	inv = pship["inventory"]["items"]
	pos = pship["pos"]
	omap = map.objmap(pos["system"])
	otile = omap.get(pos["x"],pos["y"])
	if "items" not in otile: raise error.User("This tile doesn't have any items.")
	for item,amount in titems.items():
		available = otile["items"].get(item,-1)
		if available == -1: continue
		size = items.size(item)
		space = pship.get_space()
		amount = min(available,space//size)
		amount = max(amount,0)
		inv.add(item,amount)
		otile["items"][item] -= amount
		if otile["items"].get(item) == 0:
			del otile["items"][item]
	if not len(otile["items"]):
		del otile["items"]
	pship.get_space()
	pship.save()
	omap.set(pos["x"],pos["y"],otile)
	omap.save()