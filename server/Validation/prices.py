from server import defs
def init():
	#industry items traded?
	for name,data in defs.structures.items():
		if data["type"] != "planet": continue
		industry_items = []
		traded_items = []
		for ind in data["industries"]:
			ind_def = defs.industries2[ind["name"]]
			for item in ind_def["input"].keys():
				if item not in industry_items:
					industry_items.append(item)
			for item in ind_def["output"].keys():
				if item not in industry_items:
					industry_items.append(item)
		for item in data.get_prices().keys():
			if item not in traded_items:
				traded_items.append(item)
		for item in industry_items:
			if item not in traded_items:
				print("Structure",data["name"],"has industry related to item",item,"but doesn't trade it.")
	#pricelists
	names = set()
	for name,data in defs.predefined_structures.items():
		for name2 in data["market"]["lists"]:
			names.add(name2)
	for name in defs.price_lists.keys():
		if name not in names:
			print("Pricelist "+name+" isn't in use.")