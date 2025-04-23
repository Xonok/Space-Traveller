from . import api
from server import defs,ship

#kind of annoying that everything has to take udata and cdata
#just udata alone would probably be fine
def get_characters(udata,cdata):
	data = {}
	for name in udata["characters"]:
		cdata = defs.characters[name]
		pship = ship.get(cdata["ship"])
		data[name] = {
			"active_ship": pship
		}
	return data
def get_active_character(udata,cdata):
	return udata["active_character"]
def get_starters(udata,cdata):
	return defs.starters

api.register_query("characters",get_characters)
api.register_query("active-character",get_active_character)
api.register_query("starters",get_starters)

api.register_command("get-characters","characters","active-character","starters")
api.register_command("make-character","characters")