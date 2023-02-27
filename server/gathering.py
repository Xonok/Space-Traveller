import re,time,random
from . import defs,error,func,ship,map,items,tick

tile_max_resource = 100
tile_resource_regen = 2

def gather(user,reduce=True):
	x = user["pos"]["x"]
	y = user["pos"]["y"]
	system = user["pos"]["system"]
	tiles = map.tilemap(system)
	otiles = map.objmap(system)
	tile = tiles.get(x,y)
	otile = otiles.get(x,y)
	terrain = tile["terrain"]
	if terrain not in defs.gatherables: raise error.User("This tile doesn't contain any gatherables.")
	process = defs.gatherables[terrain]
	if "item_or" in process:
		if not set.intersection(set(user.get_gear()),set(process["item_or"])):
			raise error.User("Don't have the proper equipment to harvest from this tile.")
	update_resources(otiles,x,y)
	remaining = get_resource_amount(otiles,x,y)
	output = items.Items()
	for item,amount in process["output"].items():
		output.add(item,calculate(amount))
	if "bonus" in process:
		for gear,amount in process["bonus"].items():
			if gear in user.get_gear():
				output.add(item,calculate(amount))
	if not len(output): return
	for item,amount in output.items():
		amount = min(user.get_space(),amount,remaining)
		amount = max(amount,0)
		if not amount: continue
		user.get_items().add(item,amount)
		if reduce:
			reduce_resource(otiles,x,y,amount)
	if "extra" in process:
		for item,data in process["extra"].items():
			if data["item"] in user.get_gear() and random.randint(1,data["chance"]) == 1:
				amount = min(user.get_space(),calculate(data["amount"]))
				amount = max(amount,0)
				if not amount: continue
				user.get_items().add(item,amount)
	user.save()
def calculate(amount):
	components = re.split("(\+)|(\-)",amount)
	result = 0
	sign = "+"
	for c in components:
		change = 0
		if c == None: continue
		if c == "+" or c == "-":
			sign = c
		elif "d" in c:
			dice,sides = c.split("d")
			change = func.dice(dice,sides)
		else:
			change = int(c)
		if sign == "-":
			change *= -1
		result += change
	return result
def update_resources(otiles,x,y):
	otile = otiles.get(x,y)
	if "timestamp" not in otile: return
	now = time.time()
	ticks = tick.ticks_since(otile["timestamp"],"long")
	ticks = max(ticks,0)
	for i in range(ticks):
		otile["resource_amount"] += tile_resource_regen
		if otile["resource_amount"] >= tile_max_resource:
			del otile["timestamp"]
			del otile["resource_amount"]
			break
	if "resource_amount" in otile:
		otile["timestamp"] = now
	otiles.set(x,y,otile)
	otiles.save()
def get_resource_amount(otiles,x,y):
	otile = otiles.get(x,y)
	if "resource_amount" not in otile: return tile_max_resource
	return otile["resource_amount"]
def reduce_resource(otiles,x,y,amount):
	otile = otiles.get(x,y)
	current = get_resource_amount(otiles,x,y)
	otile["resource_amount"] = current-amount
	if "timestamp" not in otile:
		otile["timestamp"] = time.time()
	otiles.set(x,y,otile)
	otiles.save()
#pship = ship.get("Xonok,harvester,1")
#gather(pship)