from . import defs,map,ship
def validate():
	positions()
	item_data()
	items()
	factories()
	predefs()
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
def item_data():
	for item,data in defs.items.items():
		if "type" not in data: print("Item",item,"has no type.")
		else:
			if data["type"] == "commodity": continue
			if data["type"] == "artifact": continue
			if "tech" not in data: print("Item",item,"has no tech level.")
			#print(item,data)
def validate_item(name,comment=""):
	if name not in defs.items and name not in defs.ship_types:
		print("Unknown item or ship:",name,comment)
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
			if "reroll" not in roll:
				validate_item(roll["item"],comment)
	#price lists
	for name,data in defs.price_lists.items():
		comment = "(price list: "+name+")"
		for item in data["items"]:
			validate_item(item,comment)
	#industries
	for name,data in defs.industries.items():
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
		if data["loot"] not in defs.loot:
			print("Unknown loot table: "+data["loot"]+" "+comment)
		for item in data["inventory"]["items"].keys():
			validate_item(item,comment+"(items)")
		for item in data["inventory"]["gear"].keys():
			validate_item(item,comment+"(gear)")
		#print(name,data)