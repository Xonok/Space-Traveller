import random,copy
from . import defs,map,error,items,ship
def drop(target):
	if "loot" not in target: return
	drop2(target["loot"],target)
def drop2(table_name,target,pickup=False):
	pos = target["pos"]
	loot_table = defs.loot[table_name]
	objmap = map.otiles(pos["system"])
	objtile = objmap.get(pos["x"],pos["y"])
	if "items" not in objtile:
		objtile["items"] = {}
	if pickup:
		prev_items = copy.deepcopy(objtile["items"])
	if "single_drop" not in loot_table:
		rerolls = linear(loot_table,objtile)
	else:
		rerolls = weighted(loot_table,objtile)
	objmap.set(pos["x"],pos["y"],objtile)
	objmap.save()
	for name,amount in rerolls.items():
		for i in range(amount):
			drop2(name,target)
	if pickup and objtile["items"]:
		to_pickup = {}
		for item,amount in objtile["items"].items():
			if item in prev_items:
				amount -= prev_items[item]
			to_pickup[item] = amount
		cdata = defs.characters.get(target["owner"])
		take({"ship":target["name"],"items":to_pickup},cdata)
def generate(table_name,items=None):
	if not items:
		items = {}
	loot_table = defs.loot[table_name]
	if "single_drop" not in loot_table:
		rerolls = linear2(loot_table,items)
	else:
		rerolls = weighted2(loot_table,items)
	for name,amount in rerolls.items():
		for i in range(amount):
			generate(name,items)
	return items
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
def linear2(loot_table,items):
	rerolls = {}
	for data in loot_table["rolls"]:
		if random.randint(1,data["rarity"]) == 1:
			item = data["item"]
			if "reroll" not in data:
				if item not in items:
					items[item] = 0
				items[item] += random.randint(data["min"],data["max"])
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
	data = random.choices(loot_table["rolls"],weights)[0]
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
def weighted2(loot_table,items):
	rerolls = {}
	weights = []
	for data in loot_table["rolls"]:
		weights.append(1/data["rarity"])
	data = random.choices(loot_table["rolls"],weights)[0]
	item = data["item"]
	if "reroll" not in data:
		if item not in items:
			items[item] = 0
		items[item] += random.randint(data["min"],data["max"])
	else:
		if item not in rerolls:
			rerolls[item] = 0
		rerolls[item] += random.randint(data["min"],data["max"])
	return rerolls
def take(data,cdata):
	pship = ship.get(data["ship"])
	if pship["owner"] != cdata["name"]: raise error.User("You don't own the ship: "+pship["name"])
	titems = data["items"]
	inv = pship["inventory"]["items"]
	pos = pship["pos"]
	omap = map.otiles(pos["system"])
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
def get(system,x,y):
	objmap = map.otiles(system)
	objtile = objmap.get(x,y)
	if "items" in objtile:
		return objtile["items"]
	return {}