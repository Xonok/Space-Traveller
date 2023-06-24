conversions = {
	"chem_plant": "refinery"
}
removals = [
	"homeworld_return_device",
	"homeworld_return_device2",
	"bp_homeworld_return_device",
	"bp_chem_plant"
]
def item_names(table,name):
	for item,amount in list(table.items()):
		if item in conversions:
			print("Updating "+item+" to "+item+" in "+name)
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