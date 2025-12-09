from server import func,defs

ship_pos = {}
sys_tile_ships = {}

#These could've been in func, but I wanted to see the function signatures.
def table_get(table,default=None,*keychain):
	last = keychain[-1]
	for name in keychain[:-1]:
		table = table.get(name)
		if not table:
			if default is None:
				raise Exception("table_get failed and no default was provided. keychain: "+str(keychain))
			return default
	return table.get(last,default)
def table_set(table,val,*keychain):
	last = keychain[-1]
	for k in keychain[:-1]:
		if k not in table:
			table[k] = {}
		table = table[k]
	table[last] = val
def table_del(table,*keychain):
	if len(keychain) == 1:
		del table[keychain[0]]
	else:
		table_del(table[keychain[0]],keychain[1:])
def table_clean(table):
	for k,v in list(table.items()):
		if type(v) is dict:
			table_clean(v)
		if type(v) is dict or type(v) is list:
			if not len(v):
				del table[k]
	
def update_ship_pos(sname,x,y,system=None):
	x = int(x)
	y = int(y)
	prev_pos = ship_pos.get(sname)
	if prev_pos:
		(px,py,psys) = prev_pos
		prev_ships = table_get(sys_tile_ships,None,psys,px,py)
		if sname in prev_ships:
			prev_ships.remove(sname)
		if system is None:
			system = psys
	if system is None:
		raise Exception("Need to provide param 'system', since the ship's previous location isn't known yet.")
	ships = table_get(sys_tile_ships,[],system,x,y)
	if sname not in ships:
		ships.append(sname)
	ship_pos[sname] = (x,y,system)
	table_set(sys_tile_ships,ships,system,x,y)
def remove_ships(snames):
	for sname in snames:
		(px,py,psys) = ship_pos[sname]
		prev_ships = table_get(sys_tile_ships,None,psys,px,py)
		prev_ships.remove(sname)
		del ship_pos[sname]
		if not len(prev_ships):
			table_clean(sys_tile_ships[psys])
def init():
	for sname,pship in defs.ships.items():
		pos = pship["pos"]
		update_ship_pos(sname,pos["x"],pos["y"],pos["system"])
