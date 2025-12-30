import copy
from server import defs

conversions = {
	"chem_plant": "refinery",
	"precursor_trinkets": "memes",
	"living_armor": "plastanium",
	"living_armor_vat": "plastanium_vat",
	"bp_living_armor_vat": "bp_plastanium_vat",
	"station_kit_storage": "kit_station_storage",
	"station_kit_portable": "kit_station_portable",
	"station_kit_mining": "kit_station_mining",
	"station_kit_military": "kit_station_military",
	"station_kit_farm": "kit_station_farm",
	"station_kit_industrial": "kit_station_industrial",
	"station_kit_logistics": "kit_station_logistics",
	"station_kit_habitat": "kit_station_habitat",
	"station_kit_trade": "kit_station_trade"
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
def check_item(table,item,name):
	base_name = item
	if item.startswith("bp_"):
		base_name = item[3:]
	if base_name in conversions:
		print("Updating "+item+" to "+conversions[base_name]+" in "+name)
		table[conversions[base_name]] = table[item]
		del table[item]
	if base_name in removals:
		print("Removing "+item+" from "+name)
		del table[item]
def item_names(table,name):
	for item in list(table.keys()):
		check_item(table,item,name)
def inventory(items,parent):
	item_names(items,parent["name"])
	parent.save()
def station(entity):
	if "blueprints" in entity:
		bp_list = entity["blueprints"]
		#Changing a list that's being iterated is bad, so let's not.
		name = entity["name"]
		for item in list(bp_list):
			if item in removals:
				print("Removed "+item+" from "+name+"(blueprints)")
				bp_list.remove(item)
			if item in conversions:
				print("Updating "+item+" to "+conversions[item]+" in "+name)
				bp_list.remove(item)
				bp_list.append(conversions[item])
	if entity["ship"] in conversions:
		entity["ship"] = conversions[entity["ship"]]
