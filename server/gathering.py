import re,time,random
from . import defs,error,func,map,items,tick,Skill,ship

tile_max_resource = 100
tile_resource_regen = 2

locks = {}
def get_mining_power(entity,cdata,terrain):
	#FIXME: currently entity must be cdata. Structures should be supported too.
	base_rate = {
		"space": 0,
		"energy": 6,
		"nebula": 6,
		"asteroids": 0,
		"exotic": 2,
		"phase": 2
	}
	total_power = base_rate[terrain]
	total_efficiency = 0
	bonuses = {}
	skill_mining = cdata["skills"].get("mining",0)
	skill_issue = 0
	if entity == cdata:
		pships = ship.gets(entity["name"])
		for name,pship in pships.items():
			gear = pship.get_gear()
			for iname,amount in gear.items():
				idata = defs.items[iname]
				tech = idata.get("tech",0)
				props = idata.get("props",{})
				power = props.get("mining_power_"+terrain,0)
				bonus = props.get("mining_bonus_"+terrain,{})
				eff = props.get("mining_efficiency",0)
				if power:
					if skill_mining < tech:
						skill_issue = max(tech,skill_issue)
					else:
						total_power += power*amount
						total_efficiency += eff*amount
						for key,val in bonus.items():
							if key not in bonuses:
								bonuses[key] = 0
							bonuses[key] += val
	else:
		for iname,amount in entity.get_gear().items():
			idata = defs.items[iname]
			tech = idata.get("tech",0)
			props = idata.get("props",{})
			power = props.get("mining_power_"+terrain,0)
			bonus = props.get("mining_bonus_"+terrain,{})
			eff = props.get("mining_efficiency",0)
			if power:
				if skill_mining < tech:
					skill_issue = max(tech,skill_issue)
				else:
					total_power += power*amount
					total_efficiency += eff*amount
					for key,val in bonus.items():
						if key not in bonuses:
							bonuses[key] = 0
						bonuses[key] += val
	efficiency = 0
	if total_power+total_efficiency:
		efficiency = total_efficiency/(total_power+total_efficiency)
	return total_power,efficiency,bonuses,skill_issue
def gather(entity,self,reduce=True,user=False):
	x = entity["pos"]["x"]
	y = entity["pos"]["y"]
	system = entity["pos"]["system"]
	tiles = map.tilemap(system)
	tile = tiles.get(x,y)
	terrain = tile["terrain"]
	cdata = defs.characters[entity["owner"]]
	owner = entity if entity["name"] not in defs.ships else cdata
	skill_mining = cdata["skills"].get("mining",0)
	if terrain not in defs.gatherables: 
		if user:
			raise error.User("There doesn't seem to be anything to harvest here.")
		return
	process = defs.gatherables[terrain]
	mining_power,efficiency,bonuses,skill_issue = get_mining_power(owner,cdata,terrain)
	if user and skill_issue and not mining_power:
		raise error.User("You don't have the mining skill to use any of your mining equipment.")
	if user and not mining_power:
		raise error.User("You need the proper equipment to mine this tile.")
	if not mining_power: return
	if user:
		now = time.time()
		if cdata["name"] in locks:
			if locks[cdata["name"]] > now:
				raise error.User("Can't collect this resource so quickly.")
			else:
				del locks[cdata["name"]]
		if "delay" in process:
			locks[cdata["name"]] = time.time()+process["delay"]
	update_resources(system,x,y)
	remaining = get_resource_amount(system,x,y)
	if user and reduce and not remaining:
		raise error.User("Nothing left to harvest.")
	if owner.get_room() == 0:
		if user:
			raise error.User("No more room left.")
		else:
			return
	output = items.Items()
	gear = entity.get_gear()
	item = process["minable"]
	idata = defs.items[item]
	price = idata["price"]
	amount = func.f2ir(100*mining_power/price)
	initial_amount = 100*mining_power/price
	total_mined = 0
	if reduce:
		amount = min(owner.get_room(),amount,remaining)
	else:
		amount = min(owner.get_room(),amount)
	amount = max(amount,0)
	owner.get_items().add(item,amount)
	total_mined += amount
	reduce_amount = func.f2ir(amount*(1-efficiency))
	if reduce:
		reduce_resource(system,x,y,amount)
	for iname,amount in bonuses.items():
		idata = defs.items[iname]
		price = idata["price"]
		size = idata.get("size",1)
		bonus_amount = func.f2ir(100*amount/price)
		bonus_amount = min(int(owner.get_room()/size),bonus_amount)
		bonus_amount = max(bonus_amount,0)
		owner.get_items().add(iname,bonus_amount)
		total_mined += bonus_amount
	print(mining_power,price,initial_amount,amount,reduce_amount,bonuses)
	#apply bonuses
	#send message
	
	noob_factor = 1
	if cdata["level"] < 10:
		noob_factor += (9-cdata["level"])/2
	level_factor = 1/(cdata["level"]+1)
	xp_amount = func.f2ir((5+process["level"])*noob_factor*level_factor)
	msg = "Mined "+str(total_mined)+" resources."
	if xp_amount > 0:
		Skill.gain_xp_flat(cdata,xp_amount)
		msg += " Gained "+str(xp_amount)+"xp, "+str(1000-cdata["xp"])+" until next level."
	if skill_issue:
		msg += "\nItem bonus didn't work - low mining skill.("+str(skill_issue)+")"
	if self:
		self.add_message(msg)
	entity.save()
	cdata.save()
def calculate(amount):
	components = re.split(r"(\+)|(-)",amount)
	result = 0
	sign = "+"
	for c in components:
		change = 0
		if c is None: continue
		if c == "+" or c == "-":
			sign = c
		elif "d" in c:
			dice,sides = c.split("d")
			change = func.dice(dice,sides)
		else:
			change = int(c)
		if sign == "-":
			change *= -1
		result += change
	return result
def update_resources(system_name,x,y):
	system = map.system(system_name)
	otiles = map.otiles(system_name)
	otile = otiles.get(x,y)
	if "timestamp" not in otile: return
	resource_max = system.get("props",{}).get("resource",{}).get("max",tile_max_resource)
	resource_reg = system.get("props",{}).get("resource",{}).get("reg",tile_resource_regen)
	now = time.time()
	ticks = tick.ticks_since(otile["timestamp"],"long")
	ticks = max(ticks,0)
	for i in range(ticks):
		otile["resource_amount"] += resource_reg
		if otile["resource_amount"] >= resource_max:
			del otile["timestamp"]
			del otile["resource_amount"]
			break
	if "resource_amount" in otile:
		otile["timestamp"] = now
	otiles.set(x,y,otile)
	otiles.save()
def get_resource_amount(system_name,x,y):
	update_resources(system_name,x,y)
	system = map.system(system_name)
	otiles = map.otiles(system_name)
	otile = otiles.get(x,y)
	resource_max = system.get("props",{}).get("resource",{}).get("max",tile_max_resource)
	if "resource_amount" not in otile: return resource_max
	return otile["resource_amount"]
def reduce_resource(system_name,x,y,amount):
	otiles = map.otiles(system_name)
	otile = otiles.get(x,y)
	current = get_resource_amount(system_name,x,y)
	otile["resource_amount"] = current-amount
	if "timestamp" not in otile:
		otile["timestamp"] = time.time()
	otiles.set(x,y,otile)
	otiles.save()
#pship = ship.get("Xonok,harvester,1")
#gather(pship)