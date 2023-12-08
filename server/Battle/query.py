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
def get_weapons(gear):
	weapons = {}
	for iname,amount in gear.items():
		wdata = defs.weapons.get(iname)
		idata = defs.items.get(iname)
		if wdata:
			weapons[iname] = copy.deepcopy(wdata)
			weapons[iname]["amount"] = amount
			weapons[iname]["name"] = idata["name"]
			if "ammo" in wdata:
				weapons[iname]["ammo"] = wdata["ammo"]
	return weapons
def get_combat_ships(ships):
	combat_ships = {}
	for name,data in ships.items():
		weapons = get_weapons(data.get_gear())
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
	return battle
def get_ship_battle(pship):
	return ship_battle.get(pship["name"])
def get_battle_update(battle):
	if not battle: return None
	table = {
		"sides": []
	}
	for a in battle["sides"]:
		table["sides"].append({
			"combat_ships":a["combat_ships"],
			"drones/missiles":a["drones/missiles"],
			"last_log": a["logs"][-1]
		})
	return table
def log(a,msg,**kwargs):
	table = {
		"msg": msg,
		"data": kwargs
	}
	a["logs"][-1].append(table)
def in_combat(*ship_lists):
	entry = {
		"sides": []
	}
	for ship_list in ship_lists:
		for name in ship_list[0].keys():
			ship_battle[name] = entry
		entry["sides"].append({
			"ships": ship_list[0],
			"combat_ships": ship_list[1],
			"drones/missiles": {},
			"logs": []
		})
	battles.append(entry)
def targets(weapon,possible_targets,main_target):
	max_targets = weapon.get("targets",1)
	max_targets = min(max_targets,len(list(possible_targets)))
	mount = weapon["mount"]
	actual_targets = None
	if max_targets > 1:
		actual_targets = random.sample(list(possible_targets.values()),max_targets)
		if mount == "hardpoint" and main_target not in actual_targets:
			actual_targets.pop()
			actual_targets.push(main_target)
	elif mount == "hardpoint":
		actual_targets = [main_target]
	elif mount == "turret":
		actual_targets = [random.choice(list(possible_targets.values()))]
	elif mount == "hangar":
		actual_targets = []
		for i in range(weapon["shots"]):
			actual_targets.append(random.choice(list(possible_targets.values())))
	if not actual_targets: raise Exception("Empty target list for weapon")
	return actual_targets
def hit_chance(source,target,weapon):
	tstats = target.get("stats",target["ship"]["stats"])
	acc = source["stats"]["agility"]
	strack = source["stats"]["tracking"]
	track = weapon.get("tracking",0)
	size = tstats["size"]
	agi = tstats["agility"]
	n = acc+track+strack+size**0.5/10
	d = agi+agi+size**0.5/10
	d = max(d,1)
	if weapon["type"] == "pd" and target["subtype"] in ["missile","drone"]:
		n = max(n,d*0.05)
	chance = n/(n+d)
	if weapon["type"] == "laser":
		chance *= 1.5
	elif weapon["type"] == "pd":
		chance *= 2
	return chance
def damage_soak(target,vital):
	tstats = target.get("stats",target["ship"]["stats"])
	if not tstats[vital]["max"]: return 0
	soak_ratio=tstats[vital]["current"]/tstats[vital]["max"]
	return math.ceil(tstats[vital]["soak"]*soak_ratio)
def drone_missile_weapons(weapon):
	if weapon["type"] == "drone":
		predef = defs.premade_ships[weapon["ship_predef"]]
		pgear = predef["inventory"]["gear"]
		return get_weapons(pgear)
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
				"mount": weapon["mount"],
				"type": "kinetic"
			}
		}
	else:
		raise Exception("This function can only handle missile or drone weapons.")