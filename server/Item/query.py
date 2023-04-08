from server import defs

def size(item):
	if item in defs.items:
		return defs.items[item]["size"]
	if item in defs.ship_types:
		return defs.ship_types[item]["size"]
def is_ship(item):
	return item in defs.ship_types
def type(item):
	if item in defs.items:
		if "type" in defs.items[item]:
			return defs.items[item]["type"]
		return "other"
	if item in defs.ship_types:
		return "ship"
	raise Exception("Unknown kind of item: "+item)
def slot(item):
	if "slot" in defs.items[item]:
		return defs.items[item]["slot"]
	return type(item)
def net_size(item):
	if item in defs.items:
		idata = defs.items[item]
		if "props" in idata and "space_max" in idata["props"]:
			return idata["size"] - idata["props"]["space_max"]
		else:
			return idata["size"]
	elif item in defs.ship_types:
		return defs.items[item]["size"]
	else:
		raise Exception("Unknown item: "+item)