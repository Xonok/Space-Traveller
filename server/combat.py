import copy,random
from . import defs,ship
#in seconds
time_per_tick = 60*5 # 5 minutes per tick. Used for armor regeneration, actual combat can happen faster.

def make_scale(max,soak,resist):
	return {
		"max": max,
		"current": max,
		"soak": soak,		#flat damage reduction
		"resist": resist	#percent damage reduction
	}
def combat_check(ship):
	if "combat_stats" not in ship:
		ship_type = defs.ship_types[ship["type"]]
		ship["combat_stats"] = {
			"size": ship_type["size"],
			"scales": {
				"hull": make_scale(ship_type["hull"],7,30)
			},
			"speed": ship_type["speed"],
			"agility": ship_type["agility"]
		}
def get_weapons(ship):
	gear = ship["inventory"]["gear"]
	weapons = {}
	for item,amount in gear.items():
		if item in defs.weapons:
			weapons[item] = copy.deepcopy(defs.weapons[item])
			weapons[item]["amount"] = amount
	return weapons
def shoot(source,target,weapons):
	sstats = source["combat_stats"]
	tstats = target["combat_stats"]
	for name,data in weapons.items():
		if data["mount"] == "hardpoint":
			accuracy = sstats["agility"]
		else:
			raise Exception("Weapon mounts other than hardpoint not implemented.")
		n = accuracy*tstats["size"]**0.5/10
		d = tstats["agility"]*tstats["agility"]/10
		chance = 1-n/d
		for i in range(data["amount"]*data["shots"]):
			roll = 1-random.random()
			if chance < roll:
				print("evasion chance",round(chance,2),"roll",round(roll,2),"hit",data["damage"]*10,"damage")
				hit(source,target,data["damage"])
				if tstats["scales"]["hull"]["current"] <= 0: continue
			else:
				print("evasion chance",round(chance,2),"roll",round(roll,2),"miss")
	if tstats["scales"]["hull"]["current"] <= 0:
		print("Target is dead")
	#target.save()
def hit(source,target,total_damage):
	cstats = source["combat_stats"]
	total_damage *= 10
	for stat,data in cstats["scales"].items():
		if total_damage <= 0: continue
		damage = total_damage
		soaked = min(damage,data["soak"])
		damage -= soaked
		resisted = round(damage*data["resist"]/100.)
		damage -= resisted
		damage = min(damage,data["current"])
		data["current"] -= damage
		total_damage -= damage
		print("",str(soaked),"soaked",str(resisted),"resisted",str(damage),"to",stat)
def attack(source,target,rounds):
	combat_check(source)
	combat_check(target)
	sweapons = get_weapons(source)
	tweapons = get_weapons(target)
	for i in range(rounds):
		if target["combat_stats"]["scales"]["hull"]["current"] <= 0: continue
		print("round",str(i+1))
		shoot(source,target,sweapons)
		#shoot(target,source,tweapons)
	print(source["combat_stats"]["scales"])
def get_enemy_ships():
	if defs.players["Ark"]:
		npc = defs.players["Ark"]
	else:
		npc = defs.npc_players["Ark"]
	owned_ships = {}
	for ship_name in npc["ships"].keys():
		pship = ship.get(ship_name)
		owned_ships[pship["custom_name"]] = pship
	for ship_name in npc["ships_predefined"]:
		if ship_name not in owned_ships:
			premade = defs.premade_ships[ship_name]
			new_ship = ship.new(premade["type"],npc["name"])
			for key,value in premade.items():
				new_ship[key] = value
			print(new_ship)
			npc["ships"][new_ship["name"]] = new_ship["name"]
			owned_ships[ship_name] = new_ship
			new_ship.save()
	npc.save()
	return owned_ships
#s = ship.get("Xonok,harvester,1")
#attack(s,s,30)