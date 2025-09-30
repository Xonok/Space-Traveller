from . import api

def get_ship_pos(sname):
	return api.ship_pos[sname]
def get_map_ships(system):
	return api.sys_tile_ships[system]
def get_tile_ships(system,x,y):
	return api.table_get(api.sys_tile_ships,[],system,x,y)
#system -> ship positions
#char -> ship positions
#ship->pos