from server import ship,map,archeology,defs,items,structure,hive
import copy

def get_pos(ctx):
	return copy.deepcopy(active_ship(ctx)["pos"])
def get_vision(ctx):
	result = 3
	pships = active_ships(ctx)
	for pship in pships.values():
		pgear = pship.get_gear()
		if "highpower_scanner" in pgear:
			result = 5
	return result
def active_ship(ctx):
	return ship.get(ctx["cdata"].ship())
def active_ships(ctx):
	pships = {}
	for name in ctx["cdata"]["ships"]:
		pships[name] = ship.get(name)
	return pships
def owned_ships(ctx):
	return ship.character_ships(ctx["cdata"]["name"])
def tiles(ctx):
	pos = get_pos(ctx)
	vision = get_vision(ctx)
	return map.get_tiles(pos.get("system"),pos.get("x"),pos.get("y"),vision)
def tile(ctx):
	pos = get_pos(ctx)
	return map.get_tile(pos.get("system"),pos.get("x"),pos.get("y"),None)
def cdata(ctx):
	return ctx["cdata"]
def buttons(ctx):
	ptile = tile(ctx)
	result = {
		"gather": "initial",
		"excavate": "initial" if archeology.can_excavate(None,cdata(ctx)) else "none",
		"investigate": "initial" if archeology.can_investigate(None,cdata(ctx)) else "none",
		"loot": "initial" if len(ptile.get("items",{})) else "none"
	}
	return result
def get_structure(ctx):
	pos = get_pos(ctx)
	tstructure = structure.get(pos.get("system"),pos.get("x"),pos.get("y"))
	if not tstructure: return {}
	return {
		"name": tstructure["name"],
		"type": tstructure["type"],
		"owner": tstructure["owner"],
		"image": defs.ship_types[tstructure["ship"]]["img"]
	}
def idata(ctx):
	return items.character_itemdata(ctx["cdata"])
def hwr(ctx):
	return hive.hwr_info(ctx["cdata"])
def constellation(ctx):
	pship = active_ship(ctx)
	return defs.constellation_of[pship["pos"]["system"]]
def ship_defs(ctx):
	result = {}
	for pship in active_ships(ctx).values():
		result[pship["type"]] = defs.ship_types[pship["type"]]
	return result
def starmap(ctx):
	pship = active_ship(ctx)
	return defs.starmap[pship["pos"]["system"]]
def messages(ctx):
	return ctx["self"].get_messages()