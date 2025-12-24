import copy
from server import defs,itemdata

def station_kits():
	for item,data in defs.items.items():
		if data["type"] != "station_kit": continue
		ship_type = defs.station_kits[item]["ship"]
		shipdef = defs.ship_types[ship_type]
		data["shipdef"] = shipdef
		data["desc"] = shipdef["desc"]
def blueprints():
	for key,value in defs.blueprints.items():
		defs.items[key] = itemdata.blueprint(key,value)