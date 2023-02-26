import copy,random
from . import defs,ship,error,map,character,loot
battles = []
ship_battle = {}
def get(pship):
	if pship["name"] in ship_battle:
		return ship_battle[pship["name"]]
def start_battle(data,cdata):
	new_battle = {
		"attackers": [],
		"attackers_idle": [],
		"defenders": [],
		"defenders_idle": [],
		"logs": []
	}
	pship = ship.get(cdata.ship())
	target = ship.get(data["target"])
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
	if len(attackers) < 1 or len(defenders) < 1:
		end_battle(pbattle)
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
			guns = weapons2(pship)
			if not len(guns): continue
			target = random.choice(list(enemy_ships.values()))
			shoot(pship,target,guns,pbattle)
		for pship in enemy_ships.values():
			guns = weapons2(pship)
			if not len(guns): continue
			target = random.choice(list(ally_ships.values()))
			shoot(pship,target,guns,pbattle)
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
	if len(attackers) < 1 or len(defenders) < 1:
		end_battle(pbattle)
def shoot(source,target,guns,pbattle):
	guns = weapons2(source)
	msg = source["name"]+" attacks "+target["name"]
	pbattle["logs"].append(msg)
	for name,data in guns.items():
		wdata = defs.weapons[name]
		sstats = source["stats"]
		tstats = target["stats"]
		for i in range(data["shots"]):
			acc = sstats["agility"]
			size = tstats["size"]
			agi = tstats["agility"]
			n = acc*size**0.5/10
			d = agi**2/10
			chance = n/d
			roll = random.random()
			if chance > roll:
				hit(target,data)
			else:
				pbattle["logs"].append("miss")
	target.save()
def hit(target,data):
	if not target["name"] in ship_battle: return
	damage = data["damage"]
	damage_left = damage
	msg = str(damage_left)+" damage"
	target["stats"]["hull"]["current"] -= damage_left
	msg += ", "+str(damage_left)+" to hull."
	pbattle = ship_battle[target["name"]]
	pbattle["logs"].append(msg)
def end_battle(pbattle):
	ships = get_ships(pbattle)
	characters = {}
	for name,data in ships.items():
		owner = data["owner"]
		if owner not in characters:
			characters[owner] = 0
		if can_fight(data):
			characters[owner] += 1
		del ship_battle[name]
	for data in ships.values():
		owner = data["owner"]
		if characters[owner] < 1:
			kill(data)
	battles.remove(pbattle)
def kill(target):
	loot.drop(target)
	map.remove_ship(target)
	target["pos"] = {
		"x": -2,
		"y": -2,
		"rotation": 0,
		"system": "Megrez"
	}
	map.add_ship2(target)
	stats = target["stats"]
	stats["hull"]["current"] = stats["hull"]["max"]
	stats["armor"]["current"] = stats["armor"]["max"]
	stats["shield"]["current"] = stats["shield"]["max"]
	target.save()
