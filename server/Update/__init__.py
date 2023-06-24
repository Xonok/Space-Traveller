from . import item
from server import defs,stats
def run():
	for pship in defs.ships.values():
		item.inventory(pship)
	for tstruct in defs.structures.values():
		item.inventory(tstruct)
	for name,data in defs.ships.items():
		owner = data["owner"]
		if owner not in defs.character_ships:
			defs.character_ships[owner] = {}
		defs.character_ships[owner][name] = name
		shipdef = defs.ship_types.get(data["type"])
		if shipdef:
			data["img"] = shipdef["img"]
		stats.update_ship(data)
		data.save()
	for name,data in defs.structures.items():
		stats.update_ship(data)
		data.save()