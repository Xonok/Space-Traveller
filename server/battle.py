import copy,random
from . import defs,ship,error,map,loot,structure,quest
default_pos = {
	"x": -2,
	"y": -2,
	"rotation": 0,
	"system": "Megrez"
}
battles = []
ship_battle = {}
def get(pship):
	if pship["name"] in ship_battle:
		return ship_battle[pship["name"]]
def start_battle(data,cdata):
	pship = ship.get(cdata.ship())
	target = ship.get(data["target"])
	pos = pship["pos"]
	psystem = pos["system"]
	px = pos["x"]
	py = pos["y"]
	if not map.pos_equal(pos,target["pos"]): return error.User("The target ship is no longer here.")
	tstructure = structure.get(psystem,px,py)
	if tstructure:
		if tstructure["type"] == "planet":
			raise error.User("Can't fight on planets or starbases.")
	new_battle = {
		"attackers": [],
		"attackers_idle": [],
		"defenders": [],
		"defenders_idle": [],
		"logs": []
	}
	tile_ships = map.get_tile_ships(pship["pos"]["system"],pship["pos"]["x"],pship["pos"]["y"])
	for tship in tile_ships:
		if tship["owner"] == pship["owner"]:
			if can_fight(tship):
				new_battle["attackers"].append(tship["name"])
			else:
				new_battle["attackers_idle"].append(tship["name"])
			ship_battle[tship["name"]] = new_battle
		elif tship["owner"] == target["owner"]:
			if can_fight(tship):
				new_battle["defenders"].append(tship["name"])
			else:
				new_battle["defenders_idle"].append(tship["name"])
			ship_battle[tship["name"]] = new_battle
	battles.append(new_battle)
	raise error.Battle()
def can_fight(pship):
	pgear = pship.get_gear()
	has_weapons = False
	alive = True
	for item in pgear.keys():
		if item in defs.weapons:
			has_weapons = True
	if pship["stats"]["hull"]["current"] < 1:
		alive = False
	return has_weapons and alive
def remove(list,item):
	if item in list:
		list.remove(item)
def retreat(cdata):
	first_ship = ship.get(cdata["ships"][0])
	pbattle = ship_battle[first_ship["name"]]
	attackers = pbattle["attackers"]
	attackers_idle = pbattle["attackers_idle"]
	defenders = pbattle["defenders"]
	defenders_idle = pbattle["defenders_idle"]
	pships = ship.gets(cdata["name"])
	for pship in pships.values():
		name = pship["name"]
		remove(attackers,name)
		remove(attackers_idle,name)
		remove(defenders,name)
		remove(defenders_idle,name)
		del ship_battle[pship["name"]]
		pship["stats"]["shield"]["current"] = pship["stats"]["shield"]["max"]
	if len(attackers) < 1 or len(defenders) < 1:
		end_battle(pbattle,first_ship,False)
	raise error.Page()
def get_ships(pbattle):
	ships = {}
	if not pbattle: return ships
	for name in pbattle["attackers"]:
		ships[name] = ship.get(name)
	for name in pbattle["attackers_idle"]:
		ships[name] = ship.get(name)
	for name in pbattle["defenders"]:
		ships[name] = ship.get(name)
	for name in pbattle["defenders_idle"]:
		ships[name] = ship.get(name)
	return ships
def get_weapons(dict_ship):
	table = {}
	for pship in dict_ship.values():
		sgear = pship["inventory"]["gear"]
		for iname,amount in sgear.items():
			if iname in defs.weapons:
				if iname not in table:
					table[iname] = copy.deepcopy(defs.weapons[iname])
				for key,value in defs.items[iname].items():
					table[iname][key] = value
	return table
def weapons2(pship):
	table = {}
	sgear = pship["inventory"]["gear"]
	for iname,amount in sgear.items():
		if iname in defs.weapons:
			table[iname] = copy.deepcopy(defs.weapons[iname])
			table[iname]["count"] = amount
	return table
def attack(cdata,data):
	first_ship = ship.get(cdata.ship())
	pbattle = ship_battle[first_ship["name"]]
	logs = pbattle["logs"]
	attackers = pbattle["attackers"]
	attackers_idle = pbattle["attackers_idle"]
	defenders = pbattle["defenders"]
	defenders_idle = pbattle["defenders_idle"]
	rounds = data["rounds"]
	ships = get_ships(pbattle)
	ally_ships = {}
	enemy_ships = {}
	for pship in ships.values():
		if pship["name"] not in attackers and pship["name"] not in defenders: continue
		if pship["owner"] == first_ship["owner"]:
			ally_ships[pship["name"]] = pship
		else:
			enemy_ships[pship["name"]] = pship
	if len(ally_ships) and len(enemy_ships):
		for pship in ally_ships.values():
			shoot(pship,enemy_ships,pbattle)
		for pship in enemy_ships.values():
			shoot(pship,ally_ships,pbattle)
	for name in attackers:
		if not can_fight(ships[name]):
			attackers_idle.append(name)
	for name in defenders:
		if not can_fight(ships[name]):
			defenders_idle.append(name)
	for name in ships.keys():
		if name in attackers_idle:
			if name in attackers:
				logs.append(name+" was destroyed.")
				attackers.remove(name)
		if name in defenders_idle:
			if name in defenders:
				logs.append(name+" was destroyed.")
				defenders.remove(name)
	for ship_name in ships.keys():
		pship = ship.get(ship_name)
		pship["stats"]["shield"]["current"] += pship["stats"]["shield"]["reg"]
		if pship["stats"]["shield"]["current"] > pship["stats"]["shield"]["max"]:
			pship["stats"]["shield"]["current"] = pship["stats"]["shield"]["max"]
	if len(attackers) < 1 or len(defenders) < 1:
		for ship_name in ships.keys():
			pship = ship.get(ship_name)
			pship["stats"]["shield"]["current"] = pship["stats"]["shield"]["max"]
		end_battle(pbattle,first_ship)
def get_name(pship):
	return pship.get("custom_name") or pship.get("name")
def shoot(source,targets,pbattle):
	guns = weapons2(source)
	if not len(guns): return
	logs = pbattle["logs"]
	for name,data in guns.items():
		idata = defs.items[name]
		wdata = defs.weapons[name]
		sstats = source["stats"]
		if "charge" in wdata:
			if random.randint(1,wdata["charge"]) != 1:
				logs.append(idata["name"]+": charging...")
				continue
		logs.append(idata["name"]+": fire!")
		target_count = wdata.get("targets",1)
		if target_count > len(targets):
			target_count = len(targets)
		chosen_targets = random.sample(list(targets.values()),target_count)
		for target in chosen_targets:
			logs.append("Target: "+get_name(target))
			for i in range(data["shots"]*data["count"]):
				tstats = target["stats"]
				acc = sstats["agility"]
				size = tstats["size"]
				agi = tstats["agility"]
				n = acc*size**0.5/10
				d = agi**2/10
				n = max(n,100)
				if d == 0:
					chance = 1
				else:
					chance = n/d
				if wdata["type"] == "laser":
					chance *= 2
				roll = random.random()
				if chance > roll:
					msg = hit(target,data)
					logs.append("shot "+str(i+1)+", "+msg)
				else:
					logs.append("shot "+str(i+1)+", miss")
	target.save()
def hit(target,data):
	if not target["name"] in ship_battle: return
	stats = target["stats"]
	damage = data["damage"]
	damage_left = damage
	msg = str(damage_left)+" damage"
	if stats["shield"]["max"]:
		damage = min(stats["shield"]["current"],damage_left)
		damage_left -= damage
		stats["shield"]["current"] -= damage
		if damage:
			msg += ", "+str(damage)+" to shield"
	if stats["armor"]["max"]:
		armor_ratio = stats["armor"]["current"]/stats["armor"]["max"]
		damage = min(stats["armor"]["current"],round(stats["armor"]["soak"]*armor_ratio),damage_left)
		damage_left -= damage
		stats["armor"]["current"] -= damage
		if damage:
			msg += ", "+str(damage)+" to armor"
	damage = min(stats["hull"]["current"],damage_left)
	stats["hull"]["current"] -= damage
	damage_left -= damage
	msg += ", "+str(damage)+" to hull."
	if damage_left > 0:
		msg += " "+str(damage_left)+" damage overkill."
	return msg
def end_battle(pbattle,first_ship,do_loot=True):
	ships = get_ships(pbattle)
	characters = {}
	winners = []
	pos = copy.deepcopy(first_ship["pos"])
	prev_loot = copy.deepcopy(loot.get(pos["system"],pos["x"],pos["y"]))
	for name,data in ships.items():
		owner = data["owner"]
		if owner not in characters:
			characters[owner] = 0
		if can_fight(data):
			characters[owner] += 1
		del ship_battle[name]
	total_bounty = 0
	for data in ships.values():
		owner = data["owner"]
		if characters[owner] < 1:
			total_bounty += kill(data)
			for name in characters.keys():
				if characters[name] > 0:
					cdata = defs.characters.get(name)
					predef =  defs.premade_ships.get(data.get("predef"))
					quest.update_targets_killed(cdata,predef)
		else:
			winners.append(data)
	if do_loot:
		for winner in winners:
			current_loot = copy.deepcopy(loot.get(pos["system"],pos["x"],pos["y"]))
			for item,amount in prev_loot.items():
				current_loot[item] -= amount
			if not len(current_loot): break
			cdata = defs.characters.get(winner["owner"])
			if cdata:
				loot.take({"ship":winner["name"],"items":current_loot},cdata)
				cdata["credits"] += total_bounty
				total_bounty = 0
				cdata.save()
	battles.remove(pbattle)
def kill(target):
	loot.drop(target)
	map.remove_ship(target)
	owner = target["owner"]
	npc = defs.npc_characters.get(owner)
	if npc and "spawn" in npc:
		target["pos"] = copy.deepcopy(npc["spawn"])
	else:
		target["pos"] = copy.deepcopy(default_pos)
	map.add_ship2(target)
	pgear = target.get_gear()
	for item in pgear.keys():
		if item in defs.weapons:
			stats = target["stats"]
			stats["hull"]["current"] = 1
			stats["armor"]["current"] = 0
			stats["shield"]["current"] = stats["shield"]["max"]
			break
	target.save()
	bounty = 0
	predef = defs.premade_ships.get(target.get("predef"))
	if predef:
		bounty = predef.get("bounty",0)
	return bounty
