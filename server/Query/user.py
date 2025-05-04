from . import api
from server import defs,ship

def get_characters(udata,cdata):
	data = {}
	for name in udata["characters"]:
		cdata = defs.characters[name]
		pship = ship.get(cdata["ship"])
		data[name] = {
			"active_ship": pship
		}
	return data
def get_active_character(udata):
	return udata["active_character"]
def get_starters():
	return defs.starters

api.register_query("characters",get_characters)
api.register_query("active-character",get_active_character)
api.register_query("starters",get_starters)
