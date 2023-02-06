import time,copy
from . import defs,map,ship,error,types

homeworld_cooldown = 60*60*6 #6 hours as seconds
types.current_file = "server/hive.py"
hive_homeworld = types.make({
	"x": -2,
	"y": -2,
	"rotation": 0,
	"system": "Megrez"
},"pos")

def hwr_info(pship):
	pgear = pship.get_gear()
	if "homeworld_return_device2" in pgear:
		name = defs.items["homeworld_return_device2"]["name"]
	elif "homeworld_return_device" in pgear:
		name = defs.items["homeworld_return_device"]["name"]
	else:
		return {}
	current_charges,max_charges = hwr_charges(pship)
	return {
		"name": name,
		"charges": current_charges,
		"max_charges": max_charges,
		"time_left": hwr_time_left(pship)
	}
def hwr_charges(pship):
	pgear = pship.get_gear()
	max_charges = 0
	if "homeworld_return_device2" in pgear:
		max_charges = 2
	elif "homeworld_return_device" in pgear:
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
	if "homeworld_timestamp" not in pship:
		return "Ready"
	now = time.time()
	delta = pship["homeworld_timestamp"]+homeworld_cooldown-now
	if delta < 0:
		return "Ready"
	hours = int(delta/3600)
	minutes = int((delta/60)%60)
	seconds = int(delta%60)
	timestring = ""
	if hours > 0:
		timestring += str(hours)+"h"
	if minutes > 0:
		timestring += str(minutes)+"m"
	timestring += str(seconds)+"s"
	return timestring
def use_homeworld_return(data,pdata):
	first_ship = pdata["ships"][0]
	pship = ship.get(first_ship)
	charges,max_charges = hwr_charges(pship)
	if max_charges == 0:
		raise error.User("You don't have a homeworld device equipped.")
	if charges < 1:
		raise error.User("Not enough homeworld return charges. Next recharge in: "+hwr_time_left(pship))
	if "homeworld_timestamp" not in pship:
		pship["homeworld_timestamp"] = time.time()
	pship["homeworld_charges"] = charges-1
	map.remove_ship(pship)
	pship["pos"] = copy.deepcopy(hive_homeworld)
	map.add_ship(pship,hive_homeworld["system"],hive_homeworld["x"],hive_homeworld["y"])
	pship.save()
			