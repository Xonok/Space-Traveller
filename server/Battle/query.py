import random,copy,math
from server import map,ship,character,defs

battles = []
ship_battle = {}

def get_combat_pos(player_name):
	cdata = character.data(player_name)
	pship = ship.get(cdata.ship())
	return copy.deepcopy(pship["pos"])
def get_ships(owner,pos):
	owned_ships = {}
	all_ships = map.get_tile_ships(pos["system"],pos["x"],pos["y"])
	for data in all_ships:
		if data["owner"] == owner:
			owned_ships[data["name"]] = data
	return owned_ships
def get_combat_ship(a,name):
	return a["combat_ships"][name]
def get_weapons(gear,cdata,override=None):
	weapons = {}
	skills = cdata.get("skills",{})
	for iname,amount in gear.items():
		wdata = defs.weapons.get(iname)
		idata = defs.items.get(iname)
		if wdata:
			item_category = defs.item_categories[idata["type"]]
			tech = idata.get("tech",0)
			if override is not None:
				tech = override
			skill = item_category.get("skill")
			skill_factor = 1
			skill_lvl = skills.get(skill,0)
			if skill:
				skill_deficit = tech-skill_lvl
				if skill_deficit > 0:
					skill_factor = max(0.5**skill_deficit,0.2)
			if cdata["name"] in defs.npc_characters:
				skill_factor = 1
			weapons[iname] = copy.deepcopy(wdata)
			weapons[iname]["tech"] = tech
			weapons[iname]["damage"] = int(weapons[iname]["damage"]*skill_factor)
			weapons[iname]["damage_shield"] = int(weapons[iname].get("damage_shield",0)*skill_factor)
			weapons[iname]["damage_armor"] = int(weapons[iname].get("damage_armor",0)*skill_factor)
			weapons[iname]["damage_hull"] = int(weapons[iname].get("damage_hull",0)*skill_factor)
			weapons[iname]["amount"] = amount
			weapons[iname]["name"] = idata["name"]
			weapons[iname]["id"] = iname
			if "preload" in wdata:
				weapons[iname]["current_charge"] = wdata.get("charge",0)
			if "ammo" in wdata:
				weapons[iname]["ammo"] = wdata["ammo"]*amount
	return weapons
def get_combat_ships(ships):
	combat_ships = {}
	for name,data in ships.items():
		cdata = defs.characters[data["owner"]]
		weapons = get_weapons(data.get_gear(),cdata)
		if len(weapons) and data["stats"]["hull"]["current"] > 0:
			combat_ships[name] = {
				"weapons": weapons,
				"drones/missiles": [],
				"name": data["name"],
				"ship": data
			}
	return combat_ships
def get_battle(cdata):
	pship = ship.get(cdata.ship())
	battle = ship_battle.get(pship["name"])
	if battle:
		get_retreat_chance(battle)
		tick_ships(battle)
	return battle
def get_ship_battle(pship):
	return ship_battle.get(pship["name"])
def get_battle_update(battle,last_round=0):
	if not battle: return None
	get_retreat_chance(battle)
	table = {
		"sides": [],
		"round": 0
	}
	current_round = len(battle["sides"][0]["logs"])
	for a in battle["sides"]:
		table["sides"].append({
			"combat_ships": a["combat_ships"],
			"drones/missiles": a["drones/missiles"],
			"logs": [],
			"retreat_chance": a["retreat_chance"],
			"order": a["order"]
		})
		for i in range(last_round,current_round):
			table["sides"][-1]["logs"].append(a["logs"][i])
	table["round"] = battle["round"]
	return table
def get_retreat_chance(battle):
	rounds = len(battle["sides"][0]["logs"])
	a_wavg_spd = map.wavg_spd(battle["sides"][0]["ships"])
	b_wavg_spd = map.wavg_spd(battle["sides"][1]["ships"])
	if rounds == 0:
		chance_a = 1.
		chance_b = 1.
	else:
		chance_a = a_wavg_spd/(a_wavg_spd+b_wavg_spd)
		chance_a = chance_a*(1+chance_a)**(rounds-1)
		chance_b = b_wavg_spd/(a_wavg_spd+b_wavg_spd)
		chance_b = chance_b*(1+chance_b)**(rounds-1)
	battle["sides"][0]["retreat_chance"] = min(chance_a,1.)
	battle["sides"][1]["retreat_chance"] = min(chance_b,1.)
def log(a,msg,**kwargs):
	table = {
		"msg": msg,
		"data": kwargs
	}
	a["logs"][-1].append(table)
def in_combat(*ship_lists):
	entry = {
		"sides": [],
		"round": 0
	}
	for ship_list in ship_lists:
		for name in ship_list[0].keys():
			ship_battle[name] = entry
		entry["sides"].append({
			"ships": ship_list[0],
			"combat_ships": ship_list[1],
			"drones/missiles": {},
			"missiles.count": 0,
			"logs": []
		})
	battles.append(entry)
	return entry
def get_main_target(possible_targets):
	weights = []
	for target in possible_targets.values():
		weights.append(target["ship"]["stats"]["size"])
	return random.choices(list(possible_targets.values()),weights)[0]
def targets(weapon,possible_targets,main_target):
	max_targets = weapon.get("targets",1)
	max_targets = min(max_targets,len(list(possible_targets)))
	mount = weapon["mount"]
	actual_targets = None
	weights = []
	for target in possible_targets.values():
		weights.append(target["ship"]["stats"]["size"])
	if max_targets > 1:
		actual_targets = random.sample(list(possible_targets.values()),max_targets)
		if mount == "hardpoint" and main_target not in actual_targets:
			actual_targets.pop()
			actual_targets.push(main_target)
	elif mount == "hardpoint":
		actual_targets = [main_target]
	elif mount == "turret":
		actual_targets = random.choices(list(possible_targets.values()),weights)
	elif mount == "hangar":
		actual_targets = []
		for i in range(weapon["shots"]):
			for choice in random.choices(list(possible_targets.values()),weights):
				actual_targets.append(choice)
	if not actual_targets: raise Exception("Empty target list for weapon")
	return actual_targets
def evade_chance(source,target,weapon,rounds):
	tstats = target.get("stats",target["ship"]["stats"])
	stealth = tstats["stealth"]
	size = tstats["size"]
	base_chance = stealth/(stealth+size)
	result = 5*(base_chance)**rounds
	result = round(result*100)/100
	return result
def hit_chance(source,target,weapon):
	tstats = target.get("stats",target["ship"]["stats"])
	acc = source["stats"]["agility"]
	strack = source["stats"]["tracking"]
	wtrack = weapon.get("tracking",1)
	agi = tstats["agility"]
	n = (acc+strack)*wtrack
	d = agi+agi
	d = max(d,1)
	chance = n/(n+d)
	if weapon["type"] == "laser":
		#up to double accuracy
		mod_max = 2 
		chance_r = 1-chance
		#bonus decreases with accuracy. at 0.5 chance to hit, the bonus is *1.5
		mod_result = 1+(mod_max-1)*chance_r		
		if mod_result > 0:
			chance *= mod_result
	return chance
def damage_soak(target,vital):
	tstats = target.get("stats",target["ship"]["stats"])
	if not tstats[vital]["max"]: return 0
	soak_ratio=tstats[vital]["current"]/tstats[vital]["max"]
	return math.ceil(tstats[vital]["soak"]*soak_ratio)
def drone_missile_weapons(weapon,cdata):
	if weapon["type"] == "drone":
		predef = defs.predefined_ships[weapon["ship_predef"]]
		pgear = predef["gear"]
		return get_weapons(pgear,cdata,weapon["tech"])
	elif weapon["type"] == "missile":
		return {
			"payload": {
				"name": "payload",
				"damage": weapon["damage"],
				"shots": 1,
				"tracking": weapon["tracking"],
				"duration": weapon["duration"],
				"amount": 1,
				"self-destruct": True,
				"mount": "hardpoint",
				"type": "kinetic"
			}
		}
	else:
		raise Exception("This function can only handle missile or drone weapons.")
def name(entity):
	id = entity.get("id")
	if not id:
		id = entity["ship"]["id"]
	if "ship" in entity:
		entity = entity["ship"]
	if "custom_name" in entity:
		return entity["custom_name"]+","+str(entity["id"])
	else:
		return entity["name"]
def tick_ships(battle):
	for side in battle["sides"]:
		for pship in side["ships"].values():
			pship.tick()