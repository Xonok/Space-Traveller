import time,copy
from . import defs,map,ship,error,types

homeworld_cooldown = 60*60*6 #6 hours as seconds

def hwr_info(cdata):
	table = {}
	for name in cdata["ships"]:
		pship = ship.get(name)
		current_charges,max_charges = hwr_charges(pship)
		if not max_charges:
			table[name] = {}
		else:
			time_left,seconds = hwr_time_left(pship)
			table[name] = {
				"charges": current_charges,
				"max_charges": max_charges,
				"time_left": time_left,
				"seconds": seconds
			}
	return table
def hwr_charges(pship):
	max_charges = 0
	ship_type = defs.ship_types[pship["type"]]
	tags = ship_type.get("tags",[])
	if "hive" in tags:
		max_charges = 1
	if "homeworld_timestamp" not in pship:
		current = max_charges
	else:
		current = pship["homeworld_charges"]
		now = time.time()
		if now-pship["homeworld_timestamp"] > homeworld_cooldown:
			current += 1
			pship["homeworld_timestamp"] += homeworld_cooldown
			pship["homeworld_charges"] = current
		if current == max_charges:
			del pship["homeworld_timestamp"]
			del pship["homeworld_charges"]
	pship.save()
	return current,max_charges
def hwr_time_left(pship):
	cdata = defs.characters[pship["owner"]]
	q_done = len(cdata.get("quests_completed",{}))
	if q_done < 3:
		return "Not ready ("+str(q_done)+"/"+str(3)+" quests completed)",-1
	if "homeworld_timestamp" not in pship:
		return "Ready",0
	now = time.time()
	delta = pship["homeworld_timestamp"]+homeworld_cooldown-now
	if delta < 0:
		return "Ready",0
	hours = int(delta/3600)
	minutes = int((delta/60)%60)
	seconds = int(delta%60)
	timestring = ""
	if hours > 0:
		timestring += str(hours)+"h"
	if minutes > 0:
		timestring += str(minutes)+"m"
	timestring += str(seconds)+"s"
	return timestring,int(delta)
def use_homeworld_return(cdata):
	if len(cdata.get("quests_completed",{})) < 3:
		raise error.User("Homeworld Return unlocks when you've completed 3 quests.")
	pships = {}
	ship_charges = {}
	ship_max_charges = {}
	for name in cdata["ships"]:
		pships[name] = ship.get(name)
	for name,pship in pships.items():
		charges,max_charges = hwr_charges(pship)
		if max_charges < 1:
			raise error.User("Only hive ships can use homeworld return. "+name+" isn't a hive ship.")
		if charges < 1:
			raise error.User("Not enough Homeworld Return charges on ship: "+name)
		ship_charges[name] = charges
		ship_max_charges[name] = max_charges
	home_structure = defs.predefined_structures[cdata["home"]]
	home_pos = home_structure["pos"]
	for name,pship in pships.items():
		charges = ship_charges[name]
		if "homeworld_timestamp" not in pship:
			pship["homeworld_timestamp"] = time.time()
		pship["homeworld_charges"] = charges-1
		map.remove_ship(pship)
		pship["pos"] = copy.deepcopy(home_pos)
		map.add_ship(pship,pship["pos"]["system"],pship["pos"]["x"],pship["pos"]["y"])
		pship.save()
			