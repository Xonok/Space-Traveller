def make_scale(max,soak,resist,reg):
	return {
		"max": max,
		"current": max,
		"soak": soak,		#flat damage reduction
		"resist": resist,	#percent damage reduction
		"reg": reg
	}
def update_ship(pship):
	prev = {}
	if "stats" in pship:
		prev = pship["stats"]
	shipdef = defs.ship_types[pship["type"]]
	default = {
		"hull": make_scale(shipdef["hull"],0,0,0),
		"armor": make_scale(0,0,0,0),
		"shield": make_scale(0,0,0,0),
		"speed": shipdef["speed"],
		"agility": shipdef["agility"],
		"size": shipdef["size"]
	}
	pship["stats"] = default | prev
	stats = pship["stats"]
	stats["shield"]["max"] = 0
	stats["shield"]["reg"] = 0
	for item,amount in pship["inventory"]["gear"].items():
		idata = defs.items[item]
		props = idata.get("props",{})
		if "shield_max" in props:
			stats["shield"]["max"] += amount*props["shield_max"]
		if "shield_reg" in props:
			stats["shield"]["reg"] += amount*props["shield_reg"]
	stats["shield"]["current"] = stats["shield"]["max"]
	pship["stats"]["hull"]["max"] = shipdef["hull"]
	pship["stats"]["speed"] = default["speed"]
	pship["stats"]["agility"] = default["agility"]
	pship["stats"]["size"] = default["size"]
	pship.save()
from . import defs