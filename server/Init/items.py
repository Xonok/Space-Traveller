from server import defs

def init():
	for name,data in defs.items.items():
		type = data.get("type")
		if type in ["gun","missile","drone"] and name not in defs.weapons:
			print("No weapon entry for item: "+name)