from server import defs

def update(cdata):
	if "level" not in cdata:
		cdata["level"] = 0
	if "xp" not in cdata:
		cdata["xp"] = 0