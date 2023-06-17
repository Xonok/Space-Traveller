from server import defs
def get(name):
	if name in defs.ships:
		return defs.ships[name]
	if name in defs.structures:
		return defs.structures[name]
	raise Exception("Unknown entity: "+name)