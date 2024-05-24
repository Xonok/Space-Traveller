import re,time,random
from . import defs,error,func,map,items,tick

tile_max_resource = 100
tile_resource_regen = 2

locks = {}

def gather(entity,reduce=True,user=False):
	x = entity["pos"]["x"]
	y = entity["pos"]["y"]
	system = entity["pos"]["system"]
	tiles = map.tilemap(system)
	tile = tiles.get(x,y)
	terrain = tile["terrain"]
	if terrain not in defs.gatherables: 
		if user:
			raise error.User("There doesn't seem to be anything to harvest here.")
		return
	process = defs.gatherables[terrain]
	if "item_or" in process:
		if not set.intersection(set(entity.get_gear()),set(process["item_or"])):
			if user:
				raise error.User("Don't have the proper equipment to harvest from this tile.")
	if user:
		now = time.time()
		cdata = defs.characters[entity["owner"]]
		if cdata["name"] in locks:
			if locks[cdata["name"]] > now:
				raise error.User("Can't collect this resource so quickly.")
			else:
				del locks[cdata["name"]]
		if "delay" in process:
			locks[cdata["name"]] = time.time()+process["delay"]
	update_resources(system,x,y)
	remaining = get_resource_amount(system,x,y)
	if user and reduce and not remaining:
		raise error.User("Nothing left to harvest.")
	output = items.Items()
	for item,amount in process["output"].items():
		output.add(item,calculate(amount))
	if "bonus" in process:
		for gear,amount in process["bonus"].items():
			if gear in entity.get_gear():
				output.add(item,calculate(amount))
	if not len(output): return
	for item,amount in output.items():
		amount = min(entity.get_room(),amount,remaining)
		amount = max(amount,0)
		if not amount: continue
		entity.get_items().add(item,amount)
		if reduce:
			reduce_resource(system,x,y,amount)
	if "extra" in process:
		for item,data in process["extra"].items():
			if data["item"] in entity.get_gear() and random.randint(1,data["chance"]) == 1:
				amount = min(entity.get_room(),calculate(data["amount"]))
				amount = max(amount,0)
				if not amount: continue
				entity.get_items().add(item,amount)
	entity.save()
def calculate(amount):
	components = re.split("(\+)|(-)",amount)
	result = 0
	sign = "+"
	for c in components:
		change = 0
		if c is None: continue
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
def update_resources(system_name,x,y):
	system = map.system(system_name)
	otiles = map.otiles(system_name)
	otile = otiles.get(x,y)
	if "timestamp" not in otile: return
	resource_max = system.get("props",{}).get("resource",{}).get("max",tile_max_resource)
	resource_reg = system.get("props",{}).get("resource",{}).get("reg",tile_resource_regen)
	now = time.time()
	ticks = tick.ticks_since(otile["timestamp"],"long")
	ticks = max(ticks,0)
	for i in range(ticks):
		otile["resource_amount"] += resource_reg
		if otile["resource_amount"] >= resource_max:
			del otile["timestamp"]
			del otile["resource_amount"]
			break
	if "resource_amount" in otile:
		otile["timestamp"] = now
	otiles.set(x,y,otile)
	otiles.save()
def get_resource_amount(system_name,x,y):
	update_resources(system_name,x,y)
	system = map.system(system_name)
	otiles = map.otiles(system_name)
	otile = otiles.get(x,y)
	resource_max = system.get("props",{}).get("resource",{}).get("max",tile_max_resource)
	if "resource_amount" not in otile: return resource_max
	return otile["resource_amount"]
def reduce_resource(system_name,x,y,amount):
	otiles = map.otiles(system_name)
	otile = otiles.get(x,y)
	current = get_resource_amount(system_name,x,y)
	otile["resource_amount"] = current-amount
	if "timestamp" not in otile:
		otile["timestamp"] = time.time()
	otiles.set(x,y,otile)
	otiles.save()
#pship = ship.get("Xonok,harvester,1")
#gather(pship)