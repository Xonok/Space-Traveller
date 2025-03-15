import copy
from server import defs

conversions = {
	"chem_plant": "refinery",
	"precursor_trinkets": "memes"
}
removals = [
	"homeworld_return_device",
	"homeworld_return_device2",
	"warp_fuel",
	"warp_fuel_factory",
	"bp_homeworld_return_device",
	"bp_chem_plant",
	"bp_warp_fuel_factory"
]
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
def item_names(table,name):
	for item,amount in list(table.items()):
		if item in conversions:
			print("Updating "+item+" to "+conversions[item]+" in "+name)
			table[conversions[item]] = amount
			del table[item]
	for item,amount in list(table.items()):
		if item in removals:
			print("Removing "+item+" from "+name)
			del table[item]
def inventory(items,parent):
	item_names(items,parent["name"])
	parent.save()