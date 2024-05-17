from server import defs

def size(item):
	if item in defs.items:
		return defs.items[item]["size"]
	if item in defs.ship_types:
		return defs.ship_types[item]["size_item"]
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
		props = idata.get("props",{})
		room_max = props.get("room_max",0)
		aura_room_bonus = props.get("aura_room_bonus",0)
		result = idata["size"]-room_max-aura_room_bonus
		return result
	elif item in defs.ship_types:
		return defs.items[item]["size"]
	else:
		raise Exception("Unknown item: "+item)
def data(item):
	return defs.items.get(item)
def prop(item,prop_name):
	idata = data(item)
	props = idata.get("props",{})
	return props.get(prop_name)
def ship_prop(ship,prop_name):
	sdata = defs.ship_types[ship]
	props = sdata.get("props",{})
	return props.get(prop_name)
def ship_type(entity):
	if "ship" in entity:
		return entity["ship"]
	else:
		return entity["type"]
def equippable(item):
	itype = type(item)
	return defs.item_categories[itype].get("equip",True)