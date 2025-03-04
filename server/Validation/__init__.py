from . import items,stars

def run():
	items.init()
	validate()


#TODO: fix this mess
from server import defs,map,ship
def validate():
	item_data()
	items2()
	factories()
	predefs()
	objects() #wormholes
	weapons()
	prices()
	blueprints()
	stars.validate()
checked_item_categories = []
def item_data():
	for item,data in defs.items.items():
		if "type" not in data: print("Item",item,"has no type.")
		if not data["desc"]: print("Item",item,"has no description.")
		if data.get("type") in ["common","produced","rare","artifact","blueprint"]: continue
		if "tech" not in data: print("Item",item,"has no tech level.")
		if item in defs.ship_types: print("Item and ship_type are identical: "+item)
		#print(item,data)
items_checked = []
def validate_item(name,comment=""):
	if name in items_checked: return
	if name in defs.items:
		idata = defs.items.get(name)
		itype = idata["type"]
		
	elif name in defs.ship_types:
		idata = defs.ship_types[name]
		itype = "ship"
	else:
		print("Unknown item or ship:",name,comment)
		return
	if itype not in defs.item_categories:
		if itype not in checked_item_categories:
			checked_item_categories.append(itype)
			print("Unknown item category: "+itype)
	iprice = idata["price"]
	if iprice < 10:
		print("Item",name,"price is",iprice)
	items_checked.append(name)
def validate_loot(name,comment=""):
	if name not in defs.loot:
		print("Unknown loot table: "+name+" "+comment)
def items2():
	#characters
	for cdata in defs.characters.values():
		comment = "(character: "+cdata["name"]+")"
		for item in cdata["items"].keys():
			validate_item(item,comment+"(items)")
	#ships
	for pship in defs.ships.values():
		comment = "(ship: "+pship["name"]+")"
		validate_item(pship["type"],comment)
		for item in pship["gear"].keys():
			validate_item(item,comment+"(gear)")
	#structures
	for tstruct in defs.structures.values():
		comment = "(structure: "+tstruct["name"]+")"
		validate_item(tstruct["ship"],comment)
		for item in tstruct["items"].keys():
			validate_item(item,comment+"(items)")
		for item in tstruct["gear"].keys():
			validate_item(item,comment+"(gear)")
	#tiles
	objmaps = defs.objmaps
	for omap in objmaps.values():
		for otile in omap["tiles"].get_all():
			if "items" not in otile: continue
			for item in otile["items"].keys():
				validate_item(item,"(omap: "+omap["name"]+")")
	for omap_name,omap in objmaps.items():
		for x,col in omap["tiles"].items():
			for y,otile in col.items():
				if "items" not in otile: continue
				for item,amount in otile["items"].items():
					if amount < 0:
						print("Negative amount of "+item+" at "+omap_name+": "+x+","+y)
	#gatherables
	for tile,data in defs.gatherables.items():
		comment = "(gatherable: "+tile+")"
		for item in data.get("item_or",[]):
			validate_item(item,comment)
		validate_item(data["minable"],comment)
	#loot tables
	for name,data in defs.loot.items():
		comment = "(loot table: "+name+")"
		for roll in data["rolls"]:
			if "reroll" in roll:
				validate_loot(roll["item"],comment)
			else:
				validate_item(roll["item"],comment)
	#price lists
	for name,data in defs.price_lists.items():
		comment = "(price list: "+name+")"
		for item in data["items"]:
			validate_item(item,comment)
	#industries
	for name,data in defs.industries2.items():
		#TODO: check if type is in ["primary","secondary","tertiary","special"]
		comment = "(industry: "+name+")"
		for item in data["input"].keys():
			validate_item(item,comment)
		for item in data["output"].keys():
			validate_item(item,comment)
	#machines
	for name,data in defs.machines.items():
		comment = "(industry: "+name+")"
		validate_item(name,comment)
		for item in data["input"].keys():
			validate_item(item,comment)
		for item in data["output"].keys():
			validate_item(item,comment)
	#skill locations
	for name,data in defs.skill_locations.items():
		for skill,data2 in data.items():
			comment = "(skill_location: "+name+", skill: "+skill+")"
			if "item_req" in data2:
				for item in data2["item_req"].keys():
					if item not in defs.items:
						validate_item(item,comment)
def factories():
	for name,data in defs.machines.items():
		if name not in defs.items:
			print("Factory entry for missing item: "+name)
	for name,data in defs.items.items():
		if data.get("type") in ["factory","farm"]:
			if name not in defs.machines:
				print("Missing factory entry for item: "+name)
def predefs():
	for name,data in defs.premade_ships.items():
		comment = "(predef: "+name+")"
		validate_item(data["ship"],comment)
		if "loot" in data:
			validate_loot(data["loot"],comment)
		for item in data["gear"].keys():
			validate_item(item,comment+"(gear)")
def objects():
	for name,data in defs.objects.items():
		reqs = data.get("reqs",{})
		for key,value in reqs.items():
			if key == "quests_completed":
				if type(value) != int:
					raise Exception("Wrong type for wormhole req: "+type(value).__name__)
			else:
				raise Exception("Unknown requirement for passing through wormhole: "+key)
def weapons():
	for name,data in defs.weapons.items():
		if data["type"] == "drone":
			if "ship_predef" not in data:
				raise Exception("The drone(weapon) "+name+" needs to have a ship_predef.")
		if "ship_predef" in data and data["ship_predef"] not in defs.premade_ships:
			print("The drone(weapon) "+name+" has a ship predef that matches no premade ship: "+data["ship_predef"])
def prices():
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
def blueprints():
	for name,data in defs.blueprints.items():
		item_name = name.removeprefix("bp_")
		if item_name not in data["outputs"]:
			print("Blueprint name and item produced don't match in blueprint: "+name+", expected output: "+item_name)