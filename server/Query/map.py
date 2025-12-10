import copy
from . import api
from server import ship,defs,structure,map,archaeology,hive,Character,gathering,Entity

def get_tiles(cdata):
	vision = cdata.get_vision()
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
			if "terrain" in tile:
				del tile["terrain"]
			# tiles[x][y]["res"] = gathering.get_resource_amount(system,x,y)/gathering.get_max_resource_amount(system)
			if otile.get("landmark"):
				lm_data = Entity.landmark.get2(otile["landmark"])
				tile["landmark"] = copy.deepcopy(lm_data)
				tile["landmark"]["img"] = defs.landmark_types[lm_data["type"]]["img"]
			if "wormhole" in tile:
				tile["img"] = defs.wormhole_types.get(tile["wormhole"]["type"],{}).get("img")
				if not tile["img"]:
					tile["img"] = defs.wormhole_types["Wormhole"]["img"]
			if "items" in otile and len(otile["items"]):
				tile["items"] = True
			if len(tile):
				tiles[x][y] = tile
		if not len(tiles[x]):
			del tiles[x]
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
def get_star_wormholes(pship):
	psystem,px,py = pship.loc()
	return defs.system_data[psystem]["wormholes"]
def get_star_props(pship):
	psystem,px,py = pship.loc()
	return defs.system_data[psystem]["props"]
api.register_query("tiles",get_tiles)
api.register_query("tile",get_tile)
api.register_query("map-structure",get_map_structure)
api.register_query("hwr",get_hwr)
api.register_query("constellation",get_constellation)
api.register_query("starmap",get_starmap)
api.register_query("map-characters",get_map_characters)
api.register_query("star-wormholes",get_star_wormholes)
api.register_query("star-props",get_star_props)
