from . import defs,error,Item

def use_machine(name,stock,room,user=False):
	if name not in defs.machines:
		raise error.User("There is no machine called "+name)
	machine = defs.machines[name]
	input = machine["input"]
	output = machine["output"]
	input_room = 0
	output_room = 0
	for item,amount in input.items():
		size = Item.size(item)
		input_room += amount*size
	for item,amount in output.items():
		size = Item.size(item)
		output_room += amount*size
	if room+input_room-output_room < 0:
		if user:
			raise error.User("Not enough room to use factory.")
		else:
			return
	for item,amount in input.items():
		if not stock.get(item) >= amount:
			if user:
				raise error.User("Not enough "+defs.items[item]["name"])
			else:
				return
	for item,amount in input.items():
		stock.add(item,-amount)
	for item,amount in output.items():
		stock.add(item,amount)
	return True
def ship_use_machine(pship,item):
	cdata = defs.characters[pship["owner"]]
	factories = pship["stats"]["factories"]
	if factories[item]["cur"] < 1:	
		raise error.User("No charges left on this factory.")
	itype = Item.query.type(item)
	if itype != "factory":
		raise error.User("Not a factory, can't use in ship.")
	result = use_machine(item,cdata.get_items(),cdata.get_room(),user=True)
	if result:
		factories[item]["cur"] -= 1
	return result
def update_stats(entity):
	if entity["name"] in defs.ships:
		if "factories" not in entity["stats"]:
			entity["stats"]["factories"] = {}
		factories = entity["stats"]["factories"]
		gear = entity.get_gear()
		to_remove = []
		for item in factories.keys():
			if item not in gear:
				to_remove.append(item)
		for item in to_remove:
			del factories[item]
		for item,amount in gear.items():
			if item not in defs.machines: continue
			itype = Item.query.type(item)
			if itype != "factory": continue
			idata = defs.items[item]
			props = idata.get("props",{})
			if "manual" in props: continue
			max = props.get("factory_max",4)*8
			default = {
				"cur": max*amount,
				"max": max*amount
			}
			entry = factories.get(item,default)
			prev = entry["max"]/max
			entry["cur"] += (amount-prev)*max
			entry["max"] += (amount-prev)*max
			factories[item] = entry
	else:
		#don't care
		pass
def recharge(entity):
	factories = entity["stats"]["factories"]
	for item,data in factories.items():
		idata = defs.items[item]
		props = idata.get("props",{})
		charge = props.get("factory_charge",4)
		amount = entity.get_gear()[item]
		data["cur"] = min(data["cur"]+charge*amount,data["max"])