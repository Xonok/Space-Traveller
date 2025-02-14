import time,random
from . import defs,ship,error,loot,Item,tick,func,Skill

def investigate(server,cdata,tstructure):
	if not tstructure: raise error.User("There is nothing to excavate here.")
	if tstructure["name"] not in defs.excavation_locations: raise error.User("There is nothing to excavate here.")
	#check if scanner/skill sufficient
	loc = defs.excavation_locations[tstructure["name"]]
	max = loc["max"]
	pos = tstructure["pos"]
	used = get_tile_digs_used(tstructure)
	remaining = max-used
	server.add_message(loc["desc"])
	if remaining > 4:
		server.add_message("There is much potential for excavation here.")
	elif remaining > 2:
		server.add_message("Several ruins have been found.")
	elif remaining > 0:
		server.add_message("Some excavation is possible.")
	else:
		server.add_message("The ruins have already been excavated. However, more ruins might be found here in the future.")
def excavate(server,cdata,tstructure):
	if not tstructure: raise error.User("There is nothing to excavate here.")
	if tstructure["name"] not in defs.excavation_locations: raise error.User("There is nothing to excavate here.")
	#check if scanner/skill sufficient
	
	pos = tstructure["pos"]
	loc = defs.excavation_locations[tstructure["name"]]
	max = loc["max"]
	used = get_tile_digs_used(tstructure)
	remaining = max-used
	if remaining < 1: raise error.User("There is nothing left to excavate.")
	
	reduce_tile(tstructure)
	rolled_loot = loot.generate(loc["loot"])
	#extra loot
	site_level = loc.get("difficulty",0)
	excavate_level = cdata["skills"].get("excavation",0)
	level_diff = excavate_level - site_level
	chance = 1.2**level_diff-1
	roll = chance-random.random()
	while roll > 0:
		extra_loot = loot.generate(loc["loot"])
		for item,amount in extra_loot.items():
			if item not in rolled_loot:
				rolled_loot[item] = 0
			rolled_loot[item] += amount
		roll -= 1
	#^
	pships = ship.gets(cdata["name"])
	pship = ship.get(cdata["ship"])
	remaining = Item.action.give(rolled_loot,cdata)
	Item.action.drop(remaining,pos["system"],pos["x"],pos["y"])
	noob_factor = 1
	if cdata["level"] < 10:
		noob_factor += (9-cdata["level"])/2
	level_factor = 1/(cdata["level"]+1)
	xp_amount = func.f2ir(200*noob_factor*level_factor)
	msg = "Successful excavation."
	if xp_amount > 0:
		Skill.gain_xp_flat(cdata,xp_amount)
		msg += " Gained "+str(xp_amount)+"xp, "+str(1000-cdata["xp"])+" until next level."
	server.add_message(msg)
def can_excavate(cdata,tstructure):
	if not tstructure: return False
	if tstructure["name"] not in defs.excavation_locations: return False
	return True
can_investigate = can_excavate
def reduce_tile(tstructure):
	pos = tstructure["pos"]
	system = pos["system"]
	x = pos["x"]
	y = pos["y"]
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
	now = time.time()
	if "digs_used" not in otile:
		otile["digs_used"] = 0
	otile["digs_used"] += 1
	otile["timestamp_dig"] = otile.get("timestamp_dig",now)
	otiles.set(x,y,otile)
	otiles.save()
def get_tile_digs_used(tstructure):
	pos = tstructure["pos"]
	system = pos["system"]
	x = pos["x"]
	y = pos["y"]
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
	if "timestamp_dig" not in otile: return 0
	loc = defs.excavation_locations[tstructure["name"]]
	rarity = loc["rarity"]
	now = time.time()
	ticks = tick.ticks_since(otile["timestamp_dig"],"long")
	ticks = max(ticks,0)
	for i in range(ticks):
		if random.randint(1,rarity) == 1:
			otile["digs_used"] -= 1
			if otile["digs_used"] < 1:
				del otile["timestamp_dig"]
				del otile["digs_used"]
				break
	if "digs_used" in otile:
		otile["timestamp_dig"] = now
	otiles.set(x,y,otile)
	otiles.save()
	if "digs_used" in otile:
		return otile["digs_used"]
	return 0