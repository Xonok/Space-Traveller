from server import defs,structure,archaeology
from . import api

def get_ship_pos(sname):
	return api.reg_ships.pos[sname]
def get_map_ships(system):
	return api.reg_ships.tile[system]
def get_tile_ships(system,x,y):
	return api.table_get(api.reg_ships.tile,[],system,x,y)
def get_struct_pos(sname):
	return api.reg_structs.pos[sname]
def get_map_structs(system):
	return api.reg_structs.tile.get(system,{})
def get_tile_structure(cdata,system,x,y):
	tstructure = structure.get(system,x,y)
	if not tstructure: return
	structinfo = {}
	structinfo = {
		"name": tstructure["name"],
		"custom_name": tstructure.get("custom_name"),
		"type": tstructure["type"],
		"ship": defs.ship_types[tstructure["ship"]]["name"],
		"owner": tstructure["owner"],
		"img": defs.ship_types[tstructure["ship"]]["img"],
		"structure": True,
		"excavate": archaeology.can_excavate(cdata,tstructure)
	}
	return structinfo
def get_tile_structs(system,x,y):
	return api.table_get(api.reg_structs.tile,[],system,x,y)
def get_map_landmarks(system):
	return api.reg_landmarks.tile.get(system,{})
def get_tile_landmarks(system,x,y):
	return api.table_get(api.reg_landmarks.tile,[],system,x,y)