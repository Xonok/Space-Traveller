import _thread,random,traceback
from server import Tick,defs,Battle,map

def run():
	args = []
	for spawner_name,data in defs.spawners.items():
		if "behaviours" not in data: continue
		behaviours = data["behaviours"]
		params = data.get("params",{})
		should_continue = False
		for name in behaviours:
			if name not in behaviour_func:
				print("Unknown behaviour: "+name)
				should_continue = True
		if should_continue: continue
		
		reqs = data.get("reqs",{})
		max_spawns = reqs.get("max",1)
		groups = {}
		for i in range(max_spawns):
			ships = {}
			for predef_name,ship_names in data["ships"].items():
				for idx,ship_name in enumerate(ship_names):
					ai_tag = spawner_name+":"+predef_name+":"+str(i)+":"+str(idx)
					ships[ai_tag] = defs.tag_to_ship[ai_tag]
			groups[i] = ships
		
		for group in groups.values():
			args.append([behaviours,params,group])
		#TODO: if each args entry were a dict, it would be possible for load_balance to test their types
	Tick.load_balance(1,process,args)
def process(behaviours,params,group):
	for b in behaviours:
		func = behaviour_func[b]
		#break when one of the functions succeeds
		if func(group,params): break
def do_retreat(group,params):
	action_taken = False
	try:
		retreat_chance = params.get("retreat_chance",0)
		retreat_round = params.get("retreat_round",0)
		for name,pship in group.items():
			battle = Battle.ship_battle(pship)
			if battle:
				round = battle["round"]
				if round >= retreat_round:
					roll = random.random()
					if roll < retreat_chance:
						Battle.retreat(battle,1)
						action_taken = True
						break
	except Exception:
		print(traceback.format_exc())
	return action_taken
def do_attack(group,params):
	action_taken = False
	try:
		attack_chance = params.get("attack_chance",0)
		for name,pship in group.items():
			battle = Battle.ship_battle(pship)
			if battle:
				roll = random.random()
				if roll < attack_chance:
					Battle.do_round(battle)
					break
	except Exception:
		print(traceback.format_exc())
	return action_taken
	print("Trying to attack")
def do_move(group,params,chance=None):
	action_taken = False
	try:
		move_chance = params.get("move_chance",0)
		if chance is not None:
			move_chance = chance
		move_dist_max = params.get("move_dist_max",0)
		move_tiles = params.get("move_tiles",[])
		move_tries = params.get("move_tries",0)
		pship0 = next(iter(group.values()))
		pos = pship0["pos"]
		cdata = defs.characters[pship0["owner"]]
		if Battle.ship_battle(pship0): return
		roll = random.random()
		if roll < move_chance:
			final_x = None
			final_y = None
			for i in range(move_tries):
				d_x = random.randint(-move_dist_max,move_dist_max)
				d_y = random.randint(-move_dist_max,move_dist_max)
				terrain = get_terrain(pos["system"],pos["x"]+d_x,pos["y"]+d_y)
				if not terrain: continue
				if len(move_tiles) == 0 or terrain in move_tiles:
					final_x = pos["x"]+d_x
					final_y = pos["y"]+d_y
					break
			if final_x and final_y:
				action_taken = True
				for name,pship in group.items():
					pship.move(final_x,final_y,pship["pos"]["rotation"])
		else:
			print("Decided to not move")
	except Exception:
		print(traceback.format_exc())
	return action_taken
def do_retreatmove(group,params):
	action_taken = do_retreat(group,params)
	if action_taken:
		do_move(group,params,chance=1)
	return action_taken
def get_terrain(system_name,x,y):
	tmap = map.tilemap(system_name)
	tile = tmap.get(x,y)
	return tile.get("terrain")

behaviour_func = {
	"retreat": do_retreat,
	"attack": do_attack,
	"move": do_move,
	"retreatmove": do_retreatmove
}

_thread.start_new_thread(Tick.schedule_periodic,(5,run))

# Tick.load_balance(5,handle_fleet,data)