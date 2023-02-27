def make_scale(max,soak,resist):
	return {
		"max": max,
		"current": max,
		"soak": soak,		#flat damage reduction
		"resist": resist	#percent damage reduction
	}
def update_ship(pship):
	prev = {}
	if "stats" in pship:
		prev = pship["stats"]
	shipdef = defs.ship_types[pship["type"]]
	default = {
		"hull": make_scale(shipdef["hull"],0,0),
		"armor": make_scale(0,0,0),
		"shield": make_scale(0,0,0),
		"speed": shipdef["speed"],
		"agility": shipdef["agility"],
		"size": shipdef["size"]
	}
	pship["stats"] = default | prev
	pship["stats"]["hull"]["max"] = shipdef["hull"]
	pship["stats"]["speed"] = default["speed"]
	pship["stats"]["agility"] = default["agility"]
	pship["stats"]["size"] = default["size"]
	pship.save()
from . import defs