import _thread,random,traceback
from server import Tick,defs,Battle

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
		for b in behaviours:
			func = behaviour_func[b]
			if not func:
				print("Unknown behaviour func: "+b)
			for g in groups.values():
				#break when one of the functions triggers
				if func(g,params): break
				
		#Get the ship groups. How?
		#Problems of this sort are getting annoying, so a database-like system is probably in order.
		#Ideally I'd want all derived information to be created in some kind of handlers and fed into a central system.
		#This central system could then respond to queries.
		
		#TODO: if each args entry were a dict, it would be possible for load_balance to test their types
		args.append([behaviours,params])
	Tick.load_balance(1,process,args)
	#loop through spawners
	#check if the spawner has behaviours
	#get spawner special data for behaviours
	#make a list of params for each fleet: ships, special data
	#using scheduler, loop through behaviours, run appropriate function, stop if True
def process(behaviours,params):
	print(behaviours,params)
def do_retreat(group,params):
	action_taken = False
	try:
		retreat_chance = params.get("retreat_chance",0)
		for name,pship in group.items():
			battle = Battle.ship_battle(pship)
			if battle:
				round = battle["round"]
				if round > 0:
					roll = random.random()
					if roll < retreat_chance:
						Battle.retreat(battle,1)
						break
	except Exception:
		print(traceback.format_exc())
	return action_taken
def do_attack(group,params):
	print("Trying to attack")

behaviour_func = {
	"retreat": do_retreat,
	"attack": do_attack
}

_thread.start_new_thread(Tick.schedule_periodic,(5,run))

# Tick.load_balance(5,handle_fleet,data)