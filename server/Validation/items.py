from server import defs

def init():
	#skills
	for name,data in defs.item_categories.items():
		skill = data.get("skill")
		if skill and skill not in defs.skills:
			print("Unknown skill "+skill+" in item category "+name+".")
	#weapons
	for name,data in defs.items.items():
		type = data.get("type")
		if type in ["gun","missile","drone"] and name not in defs.weapons:
			print("No weapon entry for item: "+name)
		if type not in defs.item_categories:
			print("Item "+name+" has unknown item type: "+type)
		if type == "missile" and "duration" not in defs.weapons[name]:
			print("No duration for missile: "+name)
		if type == "drone" and "launch" not in defs.weapons[name]:
			print("No launch for drone: "+name)
	#factions
	for name,data in defs.ship_types.items():
		if data["faction"] not in defs.factions:
			print("Unknown faction on ship "+data["name"]+"("+name+"): "+data["faction"])
	#characters
	for cdata in defs.characters.values():
		comment = "(character: "+cdata["name"]+")"
		for item in cdata["items"].keys():
			validate_item(item,comment+"(items)")
	#ships
	for pship in defs.ships.values():
		comment = "(ship: "+pship["name"]+")"
		validate_item(pship["type"],comment)
		for item in pship["gear"].keys():
			validate_item(item,comment+"(gear)")
	#structures
	for tstruct in defs.structures.values():
		comment = "(structure: "+tstruct["name"]+")"
		validate_item(tstruct["ship"],comment)
		for item in tstruct["items"].keys():
			validate_item(item,comment+"(items)")
		for item in tstruct["gear"].keys():
			validate_item(item,comment+"(gear)")
	#tiles
	objmaps = defs.objmaps
	for omap in objmaps.values():
		for otile in omap["tiles"].get_all():
			if "items" not in otile: continue
			for item in otile["items"].keys():
				validate_item(item,"(omap: "+omap["name"]+")")
	for omap_name,omap in objmaps.items():
		for x,col in omap["tiles"].items():
			for y,otile in col.items():
				if "items" not in otile: continue
				for item,amount in otile["items"].items():
					if amount < 0:
						print("Negative amount of "+item+" at "+omap_name+": "+x+","+y)
	#gatherables
	for tile,data in defs.gatherables.items():
		comment = "(gatherable: "+tile+")"
		for item in data.get("item_or",[]):
			validate_item(item,comment)
		validate_item(data["minable"],comment)
	#loot tables
	for name,data in defs.loot.items():
		comment = "(loot table: "+name+")"
		for roll in data["rolls"]:
			if "reroll" in roll:
				validate_loot(roll["item"],comment)
			else:
				validate_item(roll["item"],comment)
	#price lists
	for name,data in defs.price_lists.items():
		comment = "(price list: "+name+")"
		for item in data["items"]:
			validate_item(item,comment)
	#industries
	for name,data in defs.industries2.items():
		#TODO: check if type is in ["primary","secondary","tertiary","special"]
		comment = "(industry: "+name+")"
		for item in data["input"].keys():
			validate_item(item,comment)
		for item in data["output"].keys():
			validate_item(item,comment)
	#machines
	for name,data in defs.machines.items():
		comment = "(industry: "+name+")"
		validate_item(name,comment)
		for item in data["input"].keys():
			validate_item(item,comment)
		for item in data["output"].keys():
			validate_item(item,comment)
	#skill locations
	for name,data in defs.skill_locations.items():
		for skill,data2 in data.items():
			comment = "(skill_location: "+name+", skill: "+skill+")"
			if "item_req" in data2:
				for item in data2["item_req"].keys():
					if item not in defs.items:
						validate_item(item,comment)
	#premade ships
	for name,data in defs.predefined_ships.items():
		comment = "(predef: "+name+")"
		validate_item(data["ship"],comment)
		if "loot" in data:
			validate_loot(data["loot"],comment)
		for item in data["gear"].keys():
			validate_item(item,comment+"(gear)")
	item_ship_id_unique()
	validate_slots()
items_checked = []
def validate_loot(name,comment=""):
	if name not in defs.loot:
		print("Unknown loot table: "+name+" "+comment)
def validate_item(name,comment=""):
	if name in items_checked: return
	if name in defs.items:
		idata = defs.items.get(name)
		itype = idata["type"]
		
	elif name in defs.ship_types:
		idata = defs.ship_types[name]
		itype = "ship"
	else:
		print("Unknown item or ship:",name,comment)
		return
	if itype not in defs.item_categories:
		if itype not in checked_item_categories:
			checked_item_categories.append(itype)
			print("Unknown item category: "+itype)
	iprice = idata["price"]
	if iprice < 10:
		print("Item",name,"price is",iprice)
	items_checked.append(name)
def item_ship_id_unique():
	for name in defs.items.keys():
		if name in defs.ship_types:
			print("Id for item and ship is identical: "+name)
def validate_slots():
	critical_slots = ["gun","missile","drone"]
	for name,idata in defs.ship_types.items():
		slots = idata["slots"]
		if not len(slots): continue #ignore planets and stuff
		for slot in critical_slots:
			if slot not in slots:
				print(f"Ship type {name} doesn't have a {slot} slot.")
