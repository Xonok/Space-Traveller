from . import defs,map,ship
def validate():
	positions()
def positions():
	pships = defs.ships.values()
	objmaps = defs.objmaps
	for pship in pships:
		x,y,rotation,system = pship["pos"].values()
		owner = pship["owner"]
		name = pship["name"]
		omap = map.objmap(system)
		otile = omap.get(x,y)
		owners = otile.get("ships",{})
		if owner not in owners or name not in owners[owner]:
			print(name,"should be at",system,x,y,"but isn't according to objmap.")
	for objmap in objmaps.values():
		system = objmap["name"]
		xs = objmap["tiles"]
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
