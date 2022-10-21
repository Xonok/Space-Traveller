from . import defs
def type(name):
	if not name in defs.gear_types or "type" not in defs.gear_types[name]:
		return ""
	return defs.gear_types[name]["type"]
def equipped(gtype,items):
	current = 0
	for item,amount in items.items():
		if type(item) == gtype:
			current += amount
	return current