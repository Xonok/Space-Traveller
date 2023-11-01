from . import error,defs

def entries():
	return list(defs.lore.keys())
def request(name):
	if name not in defs.lore:
		raise error.User("No lore entry called "+name)
	return defs.lore[name]