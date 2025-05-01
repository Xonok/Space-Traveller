from . import api
from server import defs,ship,map

def get_vision(cdata):
	pship = ship.get(cdata.ship())
	pships = ship.gets(cdata["name"])
	psystem,px,py = pship.loc()
	vision = 3
	tile = map.get_tile(psystem,px,py)
	ship_defs = {}
	for data in pships.values():
		ship_defs[data["type"]] = defs.ship_types[data["type"]]
		pgear = data.get_gear()
		if "highpower_scanner" in pgear:
			vision = max(vision,5)
	vision += defs.terrain[tile["terrain"]]["vision"]
	cdata["stats"]["vision"] = vision
	return vision

api.register_query("vision",get_vision)
