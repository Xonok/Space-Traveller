from . import defs,map,ship
def validate():
	positions()
	item_data()
	items()
	factories()
	predefs()
	objects() #wormholes
	weapons()
	prices()
	blueprints()
def positions():
	pships = defs.ships.values()
	objmaps = defs.objmaps
	for pship in pships:
		x,y,rotation,system = pship["pos"].values()
		owner = pship["owner"]
		name = pship["name"]
		omap = map.otiles(system)
		otile = omap.get(x,y)
		owners = otile.get("ships",{})
		if owner not in owners or name not in owners[owner]:
			print(name,"should be at",system,x,y,"but isn't according to objmap.")
	for objmap in objmaps.values():
		system = objmap["name"]
		for x,ys in objmap["tiles"].items():
			for y,otile in ys.items():
				tile_pos = {
					"x": int(x),
					"y": int(y),
					"system": system
				}
				tships = otile.get("ships")
				if tships:
					ship_lists = tships.values()
					for names in ship_lists:
						for name in names:
							pship = ship.get(name)
							pos = pship["pos"]
							if not map.pos_equal(tile_pos,pos):
								print(name,"should be at",pos["system"],pos["x"],pos["y"],"but is (also) at",system,x,y," according to objmap")
								print(system,x,y,name,tile_pos,pship["pos"])
checked_item_categories = []
def item_data():
	for item,data in defs.items.items():
		if "type" not in data: print("Item",item,"has no type.")
		elif not data["desc"]: print("Item",item,"has no description.")
		else:
			if data["type"] == "common": continue
			if data["type"] == "produced": continue
			if data["type"] == "rare": continue
			if data["type"] == "artifact": continue
			if "tech" not in data: print("Item",item,"has no tech level.")
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
def items():
	#ships
	for pship in defs.ships.values():
		comment = "(ship: "+pship["name"]+")"
		validate_item(pship["type"],comment)
		for item in pship["inventory"]["items"].keys():
			validate_item(item,comment+"(items)")
		for item in pship["inventory"]["gear"].keys():
			validate_item(item,comment+"(gear)")
	#structures
	for tstruct in defs.structures.values():
		comment = "(structure: "+tstruct["name"]+")"
		validate_item(tstruct["ship"],comment)
		for item in tstruct["inventory"]["items"].keys():
			validate_item(item,comment+"(items)")
		for item in tstruct["inventory"]["gear"].keys():
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
		for item in data["output"].keys():
			validate_item(item,comment)
		for item in data["bonus"].keys():
			validate_item(item,comment)
		for item,data2 in data.get("extra",{}).items():
			validate_item(item,comment)
			validate_item(data2["item"],comment)
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
def factories():
	for name,data in defs.machines.items():
		if name not in defs.items:
			print("Factory entry for missing item: "+name)
	for name,data in defs.items.items():
		if data.get("type") == "factory":
			if name not in defs.machines:
				print("Missing factory entry for item: "+name)
def predefs():
	for name,data in defs.premade_ships.items():
		comment = "(predef: "+name+")"
		validate_item(data["ship"],comment)
		if "loot" in data:
			validate_loot(data["loot"],comment)
		for item in data["inventory"]["items"].keys():
			validate_item(item,comment+"(items)")
		for item in data["inventory"]["gear"].keys():
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