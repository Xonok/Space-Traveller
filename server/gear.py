from . import defs
types = defs.gear_types
def type(name):
	if not name in types or "type" not in types[name]:
		return ""
	return types[name]["type"]
def equipped(gtype,items):
	current = 0
	for item,amount in items.items():
		if type(item) == gtype:
			current += amount
	return current