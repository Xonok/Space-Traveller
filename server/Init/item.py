import copy
from server import defs

def station_kits():
	for item,data in defs.items.items():
		if data["type"] != "station_kit": continue
		ship_type = defs.station_kits[item]["ship"]
		shipdef = defs.ship_types[ship_type]
		data["props"]["room"] = shipdef["room"]
		data["props"]["hull"] = shipdef["hull"]
		if "tracking" in shipdef:
			data["props"]["tracking"] = shipdef["tracking"]
		data["desc"] = shipdef["desc"]
		if len(shipdef["slots"]):
			data["props"]["slots"] = copy.deepcopy(shipdef["slots"])
		else:
			data["props"]["slots"] = "none"