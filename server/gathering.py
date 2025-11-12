import re,time,random
from . import defs,error,func,map,items,tick,Skill,ship

tile_max_resource = 100
tile_resource_regen = 2

gather_full = {}
def get_mining_power(entity,cdata,terrain):
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
							bonuses[key] += val*amount
	else:
		for iname,amount in entity.get_gear().items():
			idata = defs.items[iname]
			tech = idata.get("tech",0)
			props = idata.get("props",{})
			station_mining = props.get("station_mining",False)
			power = props.get("mining_power_"+terrain,0)
			bonus = props.get("mining_bonus_"+terrain,{})
			eff = props.get("mining_efficiency",0)
			if station_mining and power:
				if skill_mining < tech:
					skill_issue = max(tech,skill_issue)
				else:
					total_power += power*amount
					total_efficiency += eff*amount
					for key,val in bonus.items():
						if key not in bonuses:
							bonuses[key] = 0
						bonuses[key] += val*amount
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
	cname = cdata["name"]
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
	now = time.time()
	update_resources(system,x,y)
	remaining = get_resource_amount(system,x,y)
	if user and reduce and not remaining:
		raise error.User("Nothing left to harvest.")
	if owner.get_room() == 0:
		if user:
			raise error.User("No more room left.")
		else:
			return
	if user:
		base_time = 0.2
		limit = base_time*5
		full_time = max(gather_full.get(cname,0),now)
		time_to_full = full_time-now
		power_before = mining_power
		if time_to_full > 0:
			mining_power *= min(1,(limit-time_to_full)/base_time)
		gather_full[cname] = min(full_time+base_time,now+limit)
	props = entity.get("props",{})
	limits = props.get("limits",{})
	output = items.Items()
	gear = entity.get_gear()
	item = process["minable"]
	idata = defs.items[item]
	price = idata["price"]
	#determines how many credits of value 1 mining power produces.
	#players start with 6, so a value of 30 means 180 credits per click
	#before bonuses that is
	base_mining_val = 30
	amount = func.f2ir(base_mining_val*mining_power/price)
	to_limit = 9999999999
	if item in limits:
		to_limit = max(limits[item]-owner.get_items().get(item),0)
	total_mined = 0
	amount = min(owner.get_room(),amount)
	if reduce:
		amount = min(remaining,amount)
	amount = max(amount,0)
	after_limit = min(amount,to_limit)
	limit_factor = 1
	if amount:
		limit_factor = after_limit/amount
	amount = after_limit
	owner.get_items().add(item,amount)
	total_mined += amount
	reduce_amount = func.f2ir(amount*(1-efficiency))
	if reduce:
		reduce_resource(system,x,y,reduce_amount)
	for iname,amount in bonuses.items():
		idata = defs.items[iname]
		price = idata["price"]
		size = idata.get("size",1)
		to_limit2 = 9999999999
		if iname in limits:
			to_limit2 = max(limits[iname]-owner.get_items().get(iname),0)
		bonus_amount = func.f2ir(100*amount*limit_factor/price)
		bonus_amount = min(int(owner.get_room()/size),to_limit2,bonus_amount)
		bonus_amount = max(bonus_amount,0)
		owner.get_items().add(iname,bonus_amount)
		total_mined += bonus_amount
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
def get_max(system_name,x,y):
	system = map.system(system_name)
	stiles = system["tiles"]
	stile = stiles.get(x,y)
	terrain = stile.get("terrain",None)
	if not terrain: return tile_max_resource
	props = system.get("props",{}).get("resource",{})
	if "by_tile" in props and terrain in props["by_tile"]:
		props = props["by_tile"][terrain]
	result = props.get("max",tile_max_resource)
	return result
def get_reg(system_name,x,y):
	system = map.system(system_name)
	stiles = system["tiles"]
	stile = stiles.get(x,y)
	terrain = stile.get("terrain",None)
	if not terrain: return tile_resource_regen
	props = system.get("props",{}).get("resource",{})
	if "by_tile" in props and terrain in props["by_tile"]:
		props = props["by_tile"][terrain]
	result = props.get("reg",tile_resource_regen)
	return result
def update_resources(system_name,x,y):
	system = map.system(system_name)
	otiles = map.otiles(system_name)
	otile = otiles.get(x,y)
	if "timestamp" not in otile: return
	resource_max = get_max(system_name,x,y)
	# resource_max = system.get("props",{}).get("resource",{}).get("max",tile_max_resource)
	resource_reg = get_reg(system_name,x,y)
	# resource_reg = system.get("props",{}).get("resource",{}).get("reg",tile_resource_regen)
	now = time.time()
	ticks = tick.ticks_since_infloat(otile["timestamp"],"long")
	ticks = max(ticks,0)
	reg_amount = ticks*resource_reg
	int_reg_amount = int(reg_amount)
	if int_reg_amount:
		otile["resource_amount"] += int_reg_amount
		if otile["resource_amount"] >= resource_max:
			del otile["timestamp"]
			del otile["resource_amount"]
			return
		remainder_correction = (reg_amount-int_reg_amount)*tick.time_per_tick["long"]/resource_reg
		otile["timestamp"] = now-remainder_correction
		otiles.set(x,y,otile)
		otiles.save()
def get_resource_amount(system_name,x,y):
	update_resources(system_name,x,y)
	system = map.system(system_name)
	otiles = map.otiles(system_name)
	otile = otiles.get(x,y)
	resource_max = get_max(system_name,x,y)
	# resource_max = system.get("props",{}).get("resource",{}).get("max",tile_max_resource)
	if "resource_amount" not in otile: return resource_max
	return otile["resource_amount"]
def get_max_resource_amount(system_name):
	system = map.system(system_name)
	resource_max = get_max(system_name,x,y)
	# resource_max = system.get("props",{}).get("resource",{}).get("max",tile_max_resource)
	return resource_max
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