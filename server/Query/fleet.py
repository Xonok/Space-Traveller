from . import api
from server import defs,map,structure,Battle

def get_ships(cdata):
	pships = map.get_character_ships(cdata)
	return pships
def get_ship_defs(cdata,pship,pships):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	pbattle = Battle.get(cdata)
	ship_defs = {}
	for data in pships.values():
		ship_defs[data["type"]] = defs.ship_types[data["type"]]
	if tstructure:
		ship_defs[tstructure["ship"]] = defs.ship_types[tstructure["ship"]]
	if pbattle:
		for side in pbattle["sides"]:
			for name,data in side["combat_ships"].items():
				ship_defs[data["ship"]["type"]] = defs.ship_types[data["ship"]["type"]]
	return ship_defs

api.register_query("pships",get_ships)
api.register_query("ship-defs",get_ship_defs)