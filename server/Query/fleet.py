from . import api
from server import map

def get_ships(cdata):
	pships = map.get_character_ships(cdata)
	return pships

api.register_query("pships",get_ships)
