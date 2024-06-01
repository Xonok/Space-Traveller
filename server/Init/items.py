from server import defs

def init():
	for name,data in defs.items.items():
		type = data.get("type")
		if type in ["gun","missile","drone"] and name not in defs.weapons:
			print("No weapon entry for item: "+name)
		if type not in defs.item_categories:
			print("Item "+name+" has unknown item type: "+type)
		if type in ["missile"] and "duration" not in defs.weapons[name]:
			print("No duration for missile: "+name)