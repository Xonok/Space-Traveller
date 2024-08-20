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
		return defs.ship_types[item]["size_item"]
	else:
		raise Exception("Unknown item: "+item)
def data(item):
	if is_ship(item):
		return defs.ship_types.get(item)
	else:
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
def equipable(item):
	itype = type(item)
	return defs.item_categories[itype].get("equip",True)
def net_worth(cdata):
	#TODO: equipped blueprints
	#TODO: unfinished builds - average between materials and final product, weighted by progress
	result = {
		"total": 0,
		"credits": cdata["credits"],
		"ships": 0,
		"items_ship": 0,
		"stations": 0,
		"items_station": 0,
		"credits_station": 0
	}
	char_ships = defs.character_ships[cdata["name"]]
	for name in char_ships:
		entity = defs.ships[name]
		ship_def = defs.ship_types[entity["type"]]
		result["ships"] += ship_def["price"]
		for item,amount in entity["inventory"]["items"].items():
			idata = data(item)
			result["items_ship"] += idata["price"]*amount
		for item,amount in entity["inventory"]["gear"].items():
			idata = data(item)
			result["items_ship"] += idata["price"]*amount
	char_stations = defs.character_structures.get(cdata["name"])
	if char_stations:
		for name in char_stations:
			entity = defs.structures[name]
			ship_def = defs.ship_types[entity["ship"]]
			result["stations"] += ship_def["price"]
			for item,amount in entity["inventory"]["items"].items():
				idata = data(item)
				result["items_station"] += idata["price"]*amount
			for item,amount in entity["inventory"]["gear"].items():
				idata = data(item)
				result["items_station"] += idata["price"]*amount
			result["credits_station"] += entity["credits"]
	total = 0
	for amount in result.values():
		total += amount
	result["total"] = total
	return result