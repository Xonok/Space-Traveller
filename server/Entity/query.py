from server import defs,tick
def get(name):
	if name in defs.ships:
		return defs.ships[name]
	if name in defs.structures:
		return defs.structures[name]
	raise Exception("Unknown entity: "+name)
ticks_since = tick.ticks_since