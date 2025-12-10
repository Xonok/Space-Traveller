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
	return api.reg_structs.tile[system]
def get_tile_structs(system,x,y):
	return api.table_get(api.reg_structs.tile,[],system,x,y)
