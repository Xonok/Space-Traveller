def make_scale(max,soak,resist):
	return {
		"max": max,
		"current": max,
		"soak": soak,		#flat damage reduction
		"resist": resist	#percent damage reduction
	}
def update_ship(pship):
	if "stats" not in pship:
		shipdef = defs.ship_types[pship["type"]]
		pship["stats"] = {
			"hull": make_scale(shipdef["hull"],0,0),
			"armor": make_scale(0,0,0),
			"shield": make_scale(0,0,0),
			"speed": shipdef["speed"],
			"agility": shipdef["agility"],
		}
		pship.save()
from . import defs