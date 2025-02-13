import copy
from . import api
from server import ship,defs,structure

def get_tiles(cdata):
	vision = cdata["stats"]["vision"]
	pship = ship.get(cdata.ship())
	pos = pship["pos"]
	system = pos["system"]
	px = pos["x"]
	py = pos["y"]
	stiles = defs.systems[system]["tiles"]
	otiles = defs.objmaps[system]["tiles"]
	tiles = {}
	for x in range(px-vision-2,px+vision+1+2):
		if x not in tiles:
			tiles[x] = {}
		for y in range(py-vision-2,py+vision+1+2):
			tile = copy.deepcopy(stiles.get(x,y))
			otile = otiles.get(x,y)
			tiles[x][y] = tile
			if "ships" in otile:
				table = {}
				for owner,ship_names in otile["ships"].items():
					if len(ship_names):
						for ship_name in ship_names:
							pship = ship.get(ship_name)
							ship_type = defs.ship_types[pship["type"]]
							table[ship_name] = {
								"ship": ship_type["name"],
								"type": pship["type"],
								"size": ship_type["size"],
								"img": pship["img"],
								"rotation": pship["pos"]["rotation"]
							}
				tile["ships"] = table
			tstructure = structure.get(system,x,y)
			if tstructure:
				tile["structure"] = copy.deepcopy(tstructure)
				tile["structure"]["img"] = defs.ship_types[tile["structure"]["ship"]]["img"]
			if tile.get("structure") and not tstructure:
				raise Exception("Unknown structure: "+tile["structure"])
			if "wormhole" in tile:
				tile["img"] = defs.wormhole_types.get(tile["wormhole"]["type"],{}).get("img")
				if not tile["img"]:
					tile["img"] = defs.wormhole_types["Wormhole"]["img"]
			if "items" in otile and len(otile["items"]):
				tile["items"] = True
	return tiles
api.register_query("tiles",get_tiles)

#Those should be in a separate subsystem called "Command", which would define all the available commands.
api.register_command("get-location","tiles")
api.register_command("move","tiles")
api.register_command("move-relative","tiles")
api.register_command("jump","tiles")
api.register_command("homeworld-return","tiles")