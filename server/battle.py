import copy,random
from . import defs,ship,error,map,player,loot
battles = []
ship_battle = {}
def get(pship):
	if pship["name"] in ship_battle:
		return ship_battle[pship["name"]]
def start_battle(data,pdata):
	new_battle = {
		"attackers": [],
		"defenders": [],
		"logs": []
	}
	pships = ship.gets(pdata["name"])
	for pship in pships.values():
		new_battle["attackers"].append(pship["name"])
		ship_battle[pship["name"]] = new_battle
	target = ship.get(data["target"])
	defenders = map.get_player_ships(player.data(target["owner"]))
	for d_ship in defenders.values():
		new_battle["defenders"].append(d_ship["name"])
		ship_battle[d_ship["name"]] = new_battle
	battles.append(new_battle)
	raise error.Battle()
def retreat(pdata):
	first_ship = ship.get(pdata["ships"][0])
	pbattle = ship_battle[first_ship["name"]]
	pships = ship.gets(pdata["name"])
	for pship in pships.values():
		if pship["name"] in pbattle["attackers"]:
			pbattle["attackers"].remove(pship["name"])
		if pship["name"] in pbattle["defenders"]:
			pbattle["defenders"].remove(pship["name"])
		del ship_battle[pship["name"]]
	if len(pbattle["attackers"]) < 1 or len(pbattle["defenders"]) < 1:
		end_battle(pbattle)
	raise error.Page()
def end_battle(pbattle):
	for pship in pbattle["attackers"]:
		del ship_battle[pship]
	for pship in pbattle["defenders"]:
		del ship_battle[pship]
	battles.remove(pbattle)
def allies(pdata):
	first_ship = ship.get(pdata["ships"][0])
	pbattle = get(first_ship)
	if not pbattle: return {}
	pships = {}
	if first_ship["name"] in pbattle["attackers"]:
		for name in pbattle["attackers"]:
			pships[name] = ship.get(name)
	elif first_ship["name"] in pbattle["defenders"]:
		for name in pbattle["defenders"]:
			pships[name] = ship.get(name)
	return pships
def enemies(pdata):
	first_ship = ship.get(pdata["ships"][0])
	pbattle = get(first_ship)
	if not pbattle: return {}
	pships = {}
	if first_ship["name"] in pbattle["attackers"]:
		for name in pbattle["defenders"]:
			pships[name] = ship.get(name)
	elif first_ship["name"] in pbattle["defenders"]:
		for name in pbattle["attackers"]:
			pships[name] = ship.get(name)
	return pships
def weapons(dict_ship):
	table = {}
	for pship in dict_ship.values():
		sgear = pship["inventory"]["gear"]
		for iname,amount in sgear.items():
			if iname in defs.weapons:
				if iname not in table:
					table[iname] = copy.deepcopy(defs.weapons[iname])
					table[iname]["count"] = 0
				table[iname]["count"] += amount
	return table
def weapons2(pship):
	table = {}
	sgear = pship["inventory"]["gear"]
	for iname,amount in sgear.items():
		if iname in defs.weapons:
			table[iname] = copy.deepcopy(defs.weapons[iname])
			table[iname]["count"] = amount
	return table
def attack(pdata,data):
	rounds = data["rounds"]
	ally_ships = allies(pdata)
	enemy_ships = enemies(pdata)
	pship = ship.get(pdata["ship"])
	pbattle = ship_battle[pship["name"]]
	for pship in ally_ships.values():
		guns = weapons2(pship)
		if not len(guns): continue
		target = random.choice(list(enemy_ships.values()))
		shoot(pship,target,guns,pbattle)
def make_scale(max,soak,resist):
	return {
		"max": max,
		"current": max,
		"soak": soak,		#flat damage reduction
		"resist": resist	#percent damage reduction
	}
def check_stats(pship):
	if "stats" not in pship:
		shipdef = defs.ship_types[pship["type"]]
		pship["stats"] = {
			"hull": make_scale(shipdef["hull"],0,0),
			"armor": make_scale(0,0,0),
			"shield": make_scale(0,0,0),
			"speed": shipdef["hull"],
			"agility": shipdef["hull"],
		}
		pship.save()
def shoot(source,target,guns,pbattle):
	check_stats(source)
	check_stats(target)
	guns = weapons2(source)
	msg = source["name"]+" attacks "+target["name"]
	pbattle["logs"].append(msg)
	for name,data in guns.items():
		for i in range(data["shots"]):
			hit(target,data)
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
	if target["stats"]["hull"]["current"] < 1:
		msg = target["name"]+" has been destroyed."
		pbattle["logs"].append(msg)
		kill(target)
def kill(target):
	pbattle = ship_battle[target["name"]]
	if target["name"] in pbattle["attackers"]:
		pbattle["attackers"].remove(target["name"])
	if target["name"] in pbattle["defenders"]:
		pbattle["defenders"].remove(target["name"])
	del ship_battle[target["name"]]
	if len(pbattle["attackers"]) < 1 or len(pbattle["defenders"]) < 1:
		end_battle(pbattle)
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
