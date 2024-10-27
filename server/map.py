import copy,time,threading

class System(dict):
	def save(self):
		io.write2("systems",self["name"],self)
class SystemObjects(dict):
	def save(self):
		io.write2("objmaps",self["name"],self)
class World(dict):
	def add_ship(self):
		self["ships"] += 1
		self.save()
		return self["ships"]
	def save(self):
		io.write2("","world",self)
class Grid(dict):
	def __init__(self,default=None,**kwargs):
		super().__init__()
		if not default:
			default = {}
		self.default = default
		self.update(kwargs)
		self.parent = None
	def set(self,x,y,value):
		x = str(x)
		y = str(y)
		if x not in self:
			self[x] = {}
		self[x][y] = value
		if not len(value):
			del self[x][y]
		if not len(self[x]):
			del self[x]
	def get(self,x,y):
		x = str(x)
		y = str(y)
		if x not in self or y not in self[x]:
			return copy.deepcopy(self.default)
		return self[x][y]
	def get_all(self):
		list = []
		for column in self.values():
			for value in column.values():
				list.append(value)
		return list
	def save(self):
		if not self.parent: raise Exception("Parent for SaveItems not set.")
		self.parent.save()

is_moving = {}

def system(system_name):
	return defs.systems[system_name]
def tilemap(system_name):
	return defs.systems[system_name]["tiles"]
def objmap(system_name):
	return defs.objmaps[system_name]
def otiles(system_name):
	return defs.objmaps[system_name]["tiles"]
def move3(self,data,ctx):
	cdata = ctx.get("cdata")
	move2(data,cdata)
def get_terrain(system_name,x,y):
	tmap = tilemap(system_name)
	tile = tmap.get(x,y)
	return tile["terrain"]
def wavg_spd(pships):
	w_speeds = []
	for name in pships:
		data = ship.get(name)
		speed = data["stats"]["speed"]
		weight = data["stats"]["size"]
		w_speeds.append((speed,weight))
	return func.wavg(*w_speeds)
def move_relative(data,cdata,server):
	pship = ship.get(cdata.ship())
	tx,ty = data["position"]
	tx += pship["pos"]["x"]
	ty += pship["pos"]["y"]
	data["position"] = [tx,ty]
	return move2(data,cdata,server)
def move2(data,cdata,server):
	pship = ship.get(cdata.ship())
	pships = cdata["ships"]
	for name in pships:
		if name in is_moving: raise error.User("Engines need to recharge.")
	for name in pships:
		is_moving[name] = True
	psystem = pship.get_system()
	tx,ty = data["position"]
	if not pathable(psystem,tx,ty): 
		for name in pships:
			del is_moving[name]
		raise error.User("Can't move there.")
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	if tx == x and ty == y:
		for name in pships:
			del is_moving[name]
		return
	dx = tx-x
	dy = ty-y
	path = [(x,y)]
	dist = 0
	need_assist = False
	while dx != 0 or dy != 0:
		x_off = 0
		y_off = 0
		if dx > 0: x_off = 1
		if dx < 0: x_off = -1
		if dy > 0: y_off = 1
		if dy < 0: y_off = -1
		if pathable(psystem,x+x_off,y+y_off):
			pass
		elif x_off and pathable(psystem,x+x_off,y):
			y_off = 0
		elif y_off and pathable(psystem,x,y+y_off):
			x_off = 0
		elif x_off and pathable(psystem,x+x_off,y+1):
			y_off = 1
		elif x_off and pathable(psystem,x+x_off,y-1):
			y_off = -1
		elif y_off and pathable(psystem,x+1,y+y_off):
			x_off = 1
		elif y_off and pathable(psystem,x-1,y+y_off):
			x_off = -1
		else:
			need_assist = True
			break
		x += x_off
		y += y_off
		if (x,y) in path:
			need_assist = True
			break
		path.append((x,y))
		ttype = get_terrain(psystem,x-x_off,y-y_off)
		dist += defs.terrain[ttype]["move_cost"]
		dx = tx-x
		dy = ty-y
	if x == pship["pos"]["x"] and y == pship["pos"]["y"]:
		for name in pships:
			del is_moving[name]
		raise error.User("Can't find a path there. Manual assist required.")
	last = path[-1]
	pre_last = path[-2]
	final_move_x = last[0]-pre_last[0]
	final_move_y = last[1]-pre_last[1]
	wavg_speed = wavg_spd(pships)
	if wavg_speed < 1:
		for name in pships:
			del is_moving[name]
		raise error.User("Can't move because the fleet speed is too low.")
	tile_delay = 0.5
	speed_bonus = 1.2 #how much 100 speed reduces total delay
	base = dist*tile_delay
	bonus = wavg_speed*speed_bonus/100
	delay = max(0,base-bonus)
	if pship["name"] in pships:
		for s in pships:
			ship.get(s).move(x,y,func.direction(final_move_x,final_move_y))
	else:
		pship.move(x,y,func.direction(final_move_x,final_move_y))
	cdata["last_moved"] = time.time()
	cdata.save()
	if need_assist:
		server.add_message("Can't find a path there. Manual assist required.")
	def reset(*pships):
		for name in pships:
			del is_moving[name]
	if delay:
		t = threading.Timer(delay,reset,pships)
		t.start()
	else:
		for name in pships:
			del is_moving[name]
	return path,delay
def pathable(system_name,x,y):
	return "terrain" in tilemap(system_name).get(x,y)
def get_system(system_name):
	return defs.systems[system_name]
def get_tiles(system_name,px,py,radius):
	stiles = defs.systems[system_name]["tiles"]
	otiles = defs.objmaps[system_name]["tiles"]
	tiles = {}
	for x in range(px-radius,px+radius+1):
		if x not in tiles:
			tiles[x] = {}
		for y in range(py-radius,py+radius+1):
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
			tstructure = structure.get(system_name,x,y)
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
def terrain_to_resource(terrain):
	return defs.terrain[terrain]["resource"]
def get_tile(system_name,x,y):
	stiles = defs.systems[system_name]["tiles"]
	tile = copy.deepcopy(stiles.get(x,y))
	otiles = defs.objmaps[system_name]["tiles"]
	otile = otiles.get(x,y)
	tile["resource"] = terrain_to_resource(tile["terrain"])
	if tile["resource"]:
		tile["resource_amount"] = gathering.get_resource_amount(system_name,x,y)
	else:
		tile["resource_amount"] = 0
	ships = {}
	if "items" in otile:
		tile["items"] = copy.deepcopy(otile["items"])
	if "ships" in otile:
		for owner,names in otile["ships"].items():
			ship_names = copy.deepcopy(names)
			ships[owner] = []
			for name in ship_names:
				pship = ship.get(name)
				ship_type = defs.ship_types[pship["type"]]
				table = {}
				table["name"] = pship["name"]
				if "custom_name" in pship:
					table["custom_name"] = pship["custom_name"]
				table["ship"] = ship_type["name"],
				table["type"] = pship["type"]
				table["owner"] = pship["owner"]
				table["img"] = pship["img"]
				table["id"] = pship["id"]
				table["player"] = False if pship["owner"] in defs.npc_characters else True
				table["threat"] = pship["stats"]["threat"]
				table["stats"] = pship["stats"]
				ships[owner].append(table)
	if "structure" in otile:
		tile["structure"] = otile["structure"]
	tile["ships"] = ships
	if "wormhole" in tile:
		wormhole = tile["wormhole"]
		if "target" in wormhole:
			tile["jump_target"] = wormhole["target"]["system"]
		tile["img"] = "img/wormhole.png"
		if "wormhole" in tile:
			tile["wormhole"]["img"] = defs.wormhole_types.get(tile["wormhole"]["type"],{}).get("img")
			if not tile["wormhole"]["img"]:
				tile["wormhole"]["img"] = defs.wormhole_types["Wormhole"]["img"]
	return tile
def remove_ship(pship):
	system_name = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	name = pship["name"]
	tiles = defs.objmaps[system_name]["tiles"]
	tile = tiles.get(x,y)
	if "ships" in tile and pship["owner"] in tile["ships"]:
		oships = tile["ships"][pship["owner"]]
		if name in oships:
			oships.remove(name)
		if not len(oships):
			del tile["ships"][pship["owner"]]
		if not len(tile["ships"]):
			del tile["ships"]
	tiles.set(x,y,tile)
	tiles.save()
def add_ship(pship,system_name,x,y):
	name = pship["name"]
	owner = pship["owner"]
	tiles = defs.objmaps[system_name]["tiles"]
	tile = tiles.get(x,y)
	if "ships" not in tile:
		tile["ships"] = {}
	if owner not in tile["ships"]:
		tile["ships"][owner] = []
	oships = tile["ships"][owner]
	if name not in oships:
		oships.append(name)
	pship["pos"]["system"] = system_name
	pship["pos"]["x"] = x
	pship["pos"]["y"] = y
	tiles.set(x,y,tile)
	tiles.save()
def add_ship2(pship):
	add_ship(pship,pship["pos"]["system"],pship["pos"]["x"],pship["pos"]["y"])
def get_character_ships(cdata):
	owner = cdata["name"]
	pship = ship.get(cdata.ship())
	system_name = pship["pos"]["system"]
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	otiles = defs.objmaps[system_name]["tiles"]
	otile = otiles.get(x,y)
	ships = {}
	if "ships" in otile and owner in otile["ships"]:
		for shipname in otile["ships"][owner]:			
			tship = ship.get(shipname)
			tship.tick()
			if tship["owner"] == owner:
				ships[shipname] = tship
	return ships
def get_tile_ships(system_name,x,y):
	otile = otiles(system_name).get(x,y)
	ships = []
	if "ships" not in otile:
		return ships
	for ship_names in otile["ships"].values():
		for name in ship_names:
			ships.append(ship.get(name))
	return ships
def jump(self,cdata):
	for s in cdata["ships"]:
		if s in is_moving: raise error.User("Can't jump. Your engines are still charging.")
	pos = ship.get(cdata["ship"])["pos"]
	stiles = defs.systems[pos["system"]]["tiles"]
	tile = stiles.get(pos["x"],pos["y"])
	wormhole = tile.get("wormhole")
	if not wormhole:
		raise error.User("There is no wormhole here.")
	if "target" not in wormhole: raise error.User("This wormhole isn't open.")
	reqs = wormhole.get("reqs",{})
	if "quests_completed" in reqs:
		if "quests_completed" not in cdata or len(cdata["quests_completed"]) < reqs["quests_completed"]:
			raise error.User("Need to complete "+str(reqs["quests_completed"])+" quest(s) before this wormhole becomes passable.")
	w_type = wormhole["type"]
	w_def = defs.wormhole_types.get(w_type)
	if not w_def:
		raise error.User("This wormhole isn't open.")
	if not Skill.check(cdata,"warp_navigation",w_def["warp_req"]):
		raise error.User("You are too unskilled in warp navigation to traverse this wormhole.")
	w_disabled = wormhole.get("disabled")
	if w_disabled:
		raise error.User("This wormhole isn't open.")
	target = wormhole["target"]
	for s in cdata["ships"]:
		pship = ship.get(s)
		pship.jump(target)
def pos_equal(a,b):
	return a["x"] == b["x"] and a["y"] == b["y"] and a["system"] == b["system"]
def get_star_data(data):
	star = data["star"]
	sysdata = defs.system_data[star]
	result = {
		"tiles_by_terrain": {},
		"tiles": len(sysdata["tiles"]),
		"neighbours": defs.starmap[star],
		"constellation": defs.constellation_of[star],
		"planets": []
	}
	for name in sysdata["tiles_by_terrain"].keys():
		result["tiles_by_terrain"][name] = len(sysdata["tiles_by_terrain"][name])
	for name,data in sysdata["planets"].items():
		entry = {}
		entry["name"] = name
		entry["consumes"] = {}
		entry["produces"] = {}
		for item in data["consumes"]:
			idata = defs.items[item]
			entry["consumes"][item] = {
				"name": idata["name"],
				"img": idata["img"]
			}
		for item in data["produces"]:
			idata = defs.items[item]
			entry["produces"][item] = {
				"name": idata["name"],
				"img": idata["img"]
			}
		result["planets"].append(entry)
	return result
	#tiles
	#neighbours
def get_owned_structures(system,name):	
	if system not in defs.system_data: raise user.Error("No system called "+system)
	table = {}
	for name2,data in defs.system_data[system]["structures_by_owner"].get(name,{}).items():
		table[name2] = {
			"name": data["name"],
			"name_custom": data.get("custom_name",""),
			"pos": data["pos"]
		}
	return table
from . import io,defs,func,structure,ship,error,gathering,Skill