from . import api
from server import defs,ship

def get_characters(udata,cdata):
	data = {}
	for name in udata["characters"]:
		cdata = defs.characters[name]
		props = cdata.get("props",{})
		pship = ship.get(cdata["ship"])
		pships = ship.gets(cdata["name"])
		data[name] = {
			"name": name,
			"credits": cdata["credits"],
			"level": cdata["level"],
			"active_ship": pship,
			"ships": pships,
			"stats": cdata["stats"]
		}
		if "last_active" in props:
			data[name]["last_active"] = props["last_active"]
	return data
def get_active_character(udata):
	return udata["active_character"]
def get_starters():
	return defs.starters

api.register_query("characters",get_characters)
api.register_query("active-character",get_active_character)
api.register_query("starters",get_starters)
