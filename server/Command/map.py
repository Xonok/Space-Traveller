import time,threading
from server import map,ship,defs,func,error,Skill,Battle,Query,structure,exploration,map,hive,Map,Chat
from . import api

def get_location(cdata):
	if Battle.get(cdata): raise error.Battle()
is_moving = {}
def move_rel(cdata,server,dx="int",dy="int"):
	pship = ship.get(cdata.ship())
	tx = pship["pos"]["x"] + dx
	ty = pship["pos"]["y"] + dy
	return move(cdata,server,tx,ty)
def move(cdata,server,tx="int",ty="int"):
	if Battle.get(cdata): raise error.Battle()
	def reset(*snames):
		for name in snames:
			del is_moving[name]
	pship = ship.get(cdata.ship())
	snames = cdata["ships"]
	for name in snames:
		if name in is_moving: raise error.User("Engines need to recharge.")
	psystem = pship.get_system()
	if not pathable(psystem,tx,ty): raise error.User("Can't move there.")
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	if tx == x and ty == y: return
	wavg_speed = wavg_spd(snames)
	if wavg_speed < 1:
		raise error.User("Can't move because the fleet speed is too low.")
	for name in snames: 
		is_moving[name] = True
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
		if ttype:
			dist += defs.terrain[ttype]["move_cost"]
		else:
			dist += 1
		dx = tx-x
		dy = ty-y
	if x == pship["pos"]["x"] and y == pship["pos"]["y"]:
		reset(*snames)
		raise error.User("Can't find a path there. Manual assist required.")
	last = path[-1]
	pre_last = path[-2]
	final_move_x = last[0]-pre_last[0]
	final_move_y = last[1]-pre_last[1]
	tile_delay = 1
	delay = dist*tile_delay/wavg_speed*10
	future = time.time()+delay
	snames2 = None
	if pship["name"] in snames:
		for s in snames:
			ship.get(s).move(x,y,func.direction(final_move_x,final_move_y))
		snames2 = snames
	else:
		pship.move(x,y,func.direction(final_move_x,final_move_y))
		snames2 = [pship["name"]]
	Chat.map.update_ship_pos(snames2,future)
	cdata["last_moved"] = time.time()
	cdata.save()
	if need_assist:
		if server:
			server.add_message("Can't find a path there. Manual assist required.")
	if delay:
		t = threading.Timer(delay,reset,snames)
		t.start()
	else:
		reset(*snames)
	check_visit(server,cdata,pship)
	return {"delay":future}
def jump(server,cdata,pship):
	if Battle.get(cdata): raise error.Battle()
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
	Chat.map.remove_char(cdata["name"])
	for s in cdata["ships"]:
		pship = ship.get(s)
		sname = pship["name"]
		pship.jump(target)
	check_visit(server,cdata,pship)
	Chat.map.add_char(cdata["name"])
def homeworld_return(server,cdata,pship):
	hive.use_homeworld_return(cdata)
	check_visit(server,cdata,pship)
def do_get_star_data(cdata,pship):
	return {"star-data":map.get_star_data(pship)}
def do_get_map(cdata,star="str"):
	return {
		"star": defs.systems[star]
	}
api.register("get-location",get_location,"tile","tiles","map-structure","hwr","constellation","starmap","map-characters","vision","star-wormholes","star-props","character-quests","group")
api.register("move",move,"tile","tiles","map-structure","hwr","constellation","starmap","map-characters","vision")
api.register("move-relative",move_rel,"tile","tiles","map-structure","hwr","constellation","starmap","map-characters","vision")
api.register("jump",jump,"tile","tiles","map-structure","hwr","constellation","starmap","map-characters","vision","star-wormholes","star-props")
api.register("homeworld-return",homeworld_return,"tile","tiles","map-structure","hwr","constellation","starmap","map-characters","vision","star-wormholes","star-props")
api.register("get-star-data",do_get_star_data)
api.register("get-map",do_get_map)

#the amount of tiny utility functions is a bit annoying
def tilemap(system_name):
	return defs.systems[system_name]["tiles"]
def pathable(system_name,x,y):
	return "terrain" in tilemap(system_name).get(x,y)
def get_terrain(system_name,x,y):
	tmap = tilemap(system_name)
	tile = tmap.get(x,y)
	if "terrain" in tile:
		return tile["terrain"]
	return None
#TODO: this should not be calculated on the fly. Instead it should be in cdata:stats
def wavg_spd(snames):
	w_speeds = []
	for name in snames:
		data = ship.get(name)
		speed = data["stats"]["speed"]
		weight = data["stats"]["size"]
		w_speeds.append((speed,weight))
	return func.wavg(*w_speeds)
def check_visit(server,cdata,pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if tstructure:
		exploration.check_visit(cdata,tstructure["name"],server)