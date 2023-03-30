conversions = {
	"chem_plant": "refinery"
}
def item_names(table,name):
	for item,amount in list(table.items()):
		if item in conversions:
			print("Updating "+item+" to "+conversions[item]+" in "+name)
			table[conversions[item]] = amount
			del table[item]
def inventory_items(parent):
	item_names(parent["inventory"]["items"],parent["name"])
	item_names(parent["inventory"]["gear"],parent["name"])
	parent.save()