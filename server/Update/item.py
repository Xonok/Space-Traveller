import copy
from server import defs

conversions = {
	"chem_plant": "refinery",
	"precursor_trinkets": "memes",
	"living_armor": "plastanium",
	"living_armor_vat": "plastanium_vat",
	"bp_living_armor_vat": "bp_plastanium_vat"
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