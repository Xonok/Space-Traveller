import copy

def init():
	link_data()
	station_kits()
	for key,value in defs.blueprints.items():
		defs.items[key] = blueprint(key,value)
	for name,data in defs.ship_types.items():
		tags = data.get("tags",{})
		if "hive" in tags:
			data["size_item"] = int(data["size"]*0.2)
		else:
			data["size_item"] = int(data["size"]*0.4)
def link_data():
	for iname,idata in defs.items.items():
		if iname in defs.weapons:
			idata["weapon"] = defs.weapons[iname]
		if iname in defs.machines:
			idata["factory"] = defs.machines[iname]
		if iname in defs.blueprint_of:
			idata["blueprint"] = defs.blueprint_of[iname]
		if "tech" in idata:
			itype = query.type(iname)
			item_category = defs.item_categories[itype]
			skill = item_category.get("skill")
			if skill:
				idata["skill"] = defs.skills[skill]["name"]+"("+str(idata["tech"])+")"
	for iname,idata in defs.ship_types.items():
		if "tech" in idata:
			item_category = defs.item_categories["ship"]
			skill = item_category.get("skill")
			if skill:
				idata["skill"] = defs.skills[skill]["name"]+"("+str(idata["tech"])+")"
def station_kits():
	for item,data in defs.items.items():
		if data["type"] != "station_kit": continue
		ship_type = data["props"]["station"]
		shipdef = defs.ship_types[ship_type]
		data["shipdef"] = shipdef
		data["desc"] = shipdef["desc"]
def blueprint(name,data):
	output = next(iter(data["outputs"]))
	item = query.data(output)
	item_type = query.type(output)
	table = {
		"type": "blueprint",
		"bp_category": item_type,
		"name": "Blueprint: "+item["name"],
		"desc": "This is a blueprint used to make stuff in a station.",
		"img": "img/blueprint.webp",
		"size": 0,
		"price": item["price"]
	}
	if "tech" in item:
		table["tech"] = item["tech"]
	if "slots" in item:
		table["slots"] = item["slots"] #probably a convenience thing
	table["blueprint"] = data
	return table
from server import defs
from . import query