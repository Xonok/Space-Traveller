import time,threading
from server import map,ship,defs,func,error,Skill
from . import api

is_moving = {}
def move_rel(cdata,server,dx="int",dy="int"):
	pship = ship.get(cdata.ship())
	tx = pship["pos"]["x"] + dx
	ty = pship["pos"]["y"] + dy
	return move(cdata,server,tx,ty)
def move(cdata,server,tx="int",ty="int"):
	def reset(*pships):
		for name in pships:
			del is_moving[name]
	pship = ship.get(cdata.ship())
	pships = cdata["ships"]
	for name in pships:
		if name in is_moving: raise error.User("Engines need to recharge.")
	psystem = pship.get_system()
	if not pathable(psystem,tx,ty): raise error.User("Can't move there.")
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	if tx == x and ty == y: return
	wavg_speed = wavg_spd(pships)
	if wavg_speed < 1:
		raise error.User("Can't move because the fleet speed is too low.")
	for name in pships: 
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
		dist += defs.terrain[ttype]["move_cost"]
		dx = tx-x
		dy = ty-y
	if x == pship["pos"]["x"] and y == pship["pos"]["y"]:
		reset(*pships)
		raise error.User("Can't find a path there. Manual assist required.")
	last = path[-1]
	pre_last = path[-2]
	final_move_x = last[0]-pre_last[0]
	final_move_y = last[1]-pre_last[1]
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
		if server:
			server.add_message("Can't find a path there. Manual assist required.")
	if delay:
		t = threading.Timer(delay,reset,pships)
		t.start()
	else:
		reset(*pships)
	return {"delay":delay}
def jump(cdaa):
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
api.register("move",move)
api.register("move-relative",move_rel)
api.register("jump",jump)
#the amount of tiny utility functions is a bit annoying
def tilemap(system_name):
	return defs.systems[system_name]["tiles"]
def pathable(system_name,x,y):
	return "terrain" in tilemap(system_name).get(x,y)
def get_terrain(system_name,x,y):
	tmap = tilemap(system_name)
	tile = tmap.get(x,y)
	return tile["terrain"]
#TODO: this should not be calculated on the fly. Instead it should be in cdata:stats
def wavg_spd(pships):
	w_speeds = []
	for name in pships:
		data = ship.get(name)
		speed = data["stats"]["speed"]
		weight = data["stats"]["size"]
		w_speeds.append((speed,weight))
	return func.wavg(*w_speeds)