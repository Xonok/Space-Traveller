import random
from . import defs,map,error,items,ship
def drop(target):
	if "loot" not in target: return
	drop2(target["loot"],target["pos"])
def drop2(table_name,pos):
	loot_table = defs.loot[table_name]
	objmap = map.objmap(pos["system"])
	objtile = objmap.get(pos["x"],pos["y"])
	if "items" not in objtile:
		objtile["items"] = {}
	if "single_drop" not in loot_table:
		rerolls = linear(loot_table,objtile)
	else:
		rerolls = weighted(loot_table,objtile)
	objmap.set(pos["x"],pos["y"],objtile)
	objmap.save()
	for name,amount in rerolls.items():
		for i in range(amount):
			drop2(name,pos)
def linear(loot_table,objtile):
	rerolls = {}
	for data in loot_table["rolls"]:
		if random.randint(1,data["rarity"]) == 1:
			item = data["item"]
			if "reroll" not in data:
				if item not in objtile["items"]:
					objtile["items"][item] = 0
				objtile["items"][item] += random.randint(data["min"],data["max"])
			else:
				if item not in rerolls:
					rerolls[item] = 0
				rerolls[item] += random.randint(data["min"],data["max"])
	return rerolls
def weighted(loot_table,objtile):
	rerolls = {}
	weights = []
	for data in loot_table["rolls"]:
		weights.append(1/data["rarity"])
	data = random.choices(loot_table["rolls"],weights)
	item = data["item"]
	if "reroll" not in data:
		if item not in objtile["items"]:
			objtile["items"][item] = 0
		objtile["items"][item] += random.randint(data["min"],data["max"])
	else:
		if item not in rerolls:
			rerolls[item] = 0
		rerolls[item] += random.randint(data["min"],data["max"])
	return rerolls
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