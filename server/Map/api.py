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

class Registry():
	def __init__(self):
		self.pos = {}
		self.tile = {}
	def remove(self,sname):
		if not sname in self.pos: return
		(px,py,psys) = self.pos[sname]
		prev_ships = table_get(self.tile,None,psys,px,py)
		if sname in prev_ships:
			prev_ships.remove(sname)
		del self.pos[sname]
		if not len(prev_ships):
			table_clean(self.tile[psys])
	def update(self,sname,x,y,system):
		x = int(x)
		y = int(y)
		self.remove(sname)
		ships = table_get(self.tile,[],system,x,y)
		if sname not in ships:
			ships.append(sname)
		self.pos[sname] = (x,y,system)
		table_set(self.tile,ships,system,x,y)
	def removes(self,snames):
		for sname in snames:
			self.remove(sname)
reg_ships = Registry()
reg_structs = Registry()
reg_landmarks = Registry()
def update_ship_pos(sname,x,y,system):
	reg_ships.update(sname,x,y,system)
def remove_ships(enames):
	reg_ships.removes(enames)
def update_structure_pos(ename,x,y,system):
	reg_structs.update(ename,x,y,system)
def remove_structure(ename):
	reg_structs.removes([ename])
def update_landmark_pos(ename,x,y,system):
	reg_landmarks.update(ename,x,y,system)
def remove_landmark(ename):
	reg_landmarks.removes([ename])
def init():
	for ename,pship in defs.ships.items():
		pos = pship["pos"]
		update_ship_pos(ename,pos["x"],pos["y"],pos["system"])
	for ename,tstruct in defs.structures.items():
		pos = tstruct["pos"]
		update_structure_pos(ename,pos["x"],pos["y"],pos["system"])
		reg_structs.update(ename,pos["x"],pos["y"],pos["system"])
	for lname,landmark in defs.landmarks.items():
		pos = landmark["pos"]
		update_landmark_pos(ename,pos["x"],pos["y"],pos["system"])