import copy
from . import api
from server import ship,defs,structure,map,archaeology,hive,Character

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
def get_tile(pship):
	psystem,px,py = pship.loc()
	tile = map.get_tile(psystem,px,py)
	return tile
def get_map_structure(cdata,pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	structinfo = {}
	if tstructure:
		can_excavate = archaeology.can_excavate(cdata,tstructure)
		structinfo = {
			"name": tstructure["name"],
			"custom_name": tstructure.get("custom_name"),
			"type": tstructure["type"],
			"ship": defs.ship_types[tstructure["ship"]]["name"],
			"owner": tstructure["owner"],
			"img": defs.ship_types[tstructure["ship"]]["img"],
			"structure": True,
			"excavate": can_excavate
		}
	return structinfo
def get_hwr(cdata):
	return hive.hwr_info(cdata)
def get_constellation(pship):
	constellation = defs.constellation_of.get(pship["pos"]["system"])
	if not constellation:
		constellation = "Unknown"
	return constellation
def get_starmap(pship):
	return map.get_star_data_small(pship["pos"]["system"])
def get_map_characters(pship):
	psystem,px,py = pship.loc()
	tile = map.get_tile(psystem,px,py)
	return Character.query.get_tile_characters(tile)
api.register_query("tiles",get_tiles)
api.register_query("tile",get_tile)
api.register_query("map-structure",get_map_structure)
api.register_query("hwr",get_hwr)
api.register_query("constellation",get_constellation)
api.register_query("starmap",get_starmap)
api.register_query("map-characters",get_map_characters)
