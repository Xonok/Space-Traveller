from server import defs

def init():
	for name,data in defs.item_categories.items():
		skill = data.get("skill")
		if skill and skill not in defs.skills:
			print("Unknown skill "+skill+" in item category "+name+".")
	for name,data in defs.items.items():
		type = data.get("type")
		if type in ["gun","missile","drone"] and name not in defs.weapons:
			print("No weapon entry for item: "+name)
		if type not in defs.item_categories:
			print("Item "+name+" has unknown item type: "+type)
		if type in ["missile"] and "duration" not in defs.weapons[name]:
			print("No duration for missile: "+name)
	for name,data in defs.ship_types.items():
		if data["faction"] not in defs.factions:
			print("Unknown faction on ship "+data["name"]+"("+name+"): "+data["faction"])