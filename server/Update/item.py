import copy
from server import defs

conversions = {
	"chem_plant": "refinery",
	"precursor_trinkets": "memes"
}
removals = [
	"homeworld_return_device",
	"homeworld_return_device2",
	"bp_homeworld_return_device",
	"bp_chem_plant"
]
def station_kits():
	for item,data in defs.items.items():
		if data["type"] != "station_kit": continue
		ship_type = defs.station_kits[item]["ship"]
		shipdef = defs.ship_types[ship_type]
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
def inventory(parent):
	item_names(parent["inventory"]["items"],parent["name"])
	item_names(parent["inventory"]["gear"],parent["name"])
	parent.save()