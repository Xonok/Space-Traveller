import random,copy
from server import stats,error,ship,defs,loot,Item,map
from . import query,response

def start_battle(cdata,target_name,self):
	self_name = cdata["name"]
	pos = query.get_combat_pos(self_name)
	attackers = query.get_ships(self_name,pos)
	defenders = query.get_ships(ship.get(target_name)["owner"],pos)
	attackers_active = query.get_combat_ships(attackers)
	defenders_active = query.get_combat_ships(defenders)
	if not len(attackers): raise error.User("You don't have any ships here. Weird.")
	if not len(defenders): raise error.User("The ship you're trying to attack isn't here (anymore).")
	if not len(attackers_active): raise error.User("None of your ships can currently fight. Check that they have weapons and remaining hull points.")
	if not len(defenders_active):
		response.message(self,"The defending forces immediately crumble.")
		win(attackers,defenders)
		return
	query.in_combat([attackers,attackers_active],[defenders,defenders_active])
	for pship in attackers.values():
		stats.update_ship(pship)
	for pship in defenders.values():
		stats.update_ship(pship)
	response.to_battle(self)
def attack(cdata):
	battle = query.get_battle(cdata)
	if not battle: raise error.User("Your active ship isn't in any battles currently.")
	do_round(battle)
	return query.get_battle_update(cdata)
def do_round(battle):
	a = battle["sides"][0]
	b = battle["sides"][1]
	a["logs"].append([])
	b["logs"].append([])
	ships_a = a["combat_ships"]
	ships_b = b["combat_ships"]
	drones_missiles_a = a["drones/missiles"]
	drones_missiles_b = b["drones/missiles"]
	regenerate_shields(ships_a,ships_b,drones_missiles_a,drones_missiles_b)
	point_defense(a,b,drones_missiles_a,ships_a)
	point_defense(b,a,drones_missiles_b,ships_b)
	kill_drones_missiles(a)
	kill_drones_missiles(b)
	ships_fire(a,b,drones_missiles_a,ships_a)
	ships_fire(b,a,drones_missiles_b,ships_b)
	kill_drones_missiles(a)
	kill_drones_missiles(b)
	decay_drones_missiles(a)
	decay_drones_missiles(b)
	update_active_ships(a)
	update_active_ships(b)
	a_count = len(a["combat_ships"])
	b_count = len(b["combat_ships"])
	if not a_count and not b_count:
		draw(battle)
		end_battle(battle)
	elif a_count and not b_count:
		win(a["ships"],b["ships"])
		end_battle(battle)
	elif b_count and not a_count:
		win(b["ships"],a["ships"])
		end_battle(battle)
	for pship in a["ships"].values():
		stats.update_ship(pship)
	for pship in b["ships"].values():
		stats.update_ship(pship)
def regenerate_shields(*lists):
	for a in lists:
		for pship in a.values():
			amount = stats.regenerate(pship["ship"],"shield")
			if amount:
				msg = pship["name"]+" regenerated "+str(amount)+" points of shields."
				query.log(a,msg,shield_reg=amount)
def point_defense(a,b,*shooterses):
	targets = b["drones/missiles"]
	if not len(targets): return
	for shooters in shooterses:
		for pship in shooters.values():
			for name,weapon in pship["weapons"].items():
				shots_pd = weapon.get("shots_pd",0)
				for i in range(weapon["amount"]*shots_pd):
					target = random.choice(list(targets.values()))
					chance = query.hit_chance(pship["ship"],target,weapon)
					roll = random.random()
					if chance > roll:
						do_damage(pship["ship"],target,weapon["damage"],a)
					else:
						miss(pship["ship"],target,a)
def kill_drones_missiles(a):
	dead = []
	for name,target in a["drones/missiles"].items():
		if target["ship"]["stats"]["hull"]["current"] < 1:
			msg = target["subtype"]+""+target["name"]+" destroyed"
			query.log(a,msg,type=target["subtype"],destroyed=target["name"])
			query.get_combat_ship(a,target["source"])["drones/missiles"].remove(target["name"])
			dead.append(name)
	for name in dead:
		del a["drones/missiles"][name]
def ships_fire(a,b,*shooterses):
	possible_targets = b["combat_ships"]
	for shooters in shooterses:
		for pship in shooters.values():
			main_target = random.choice(list(possible_targets.values()))
			for name,weapon in pship["weapons"].items():
				shots = weapon["shots"]
				amount = weapon["amount"]
				charge = weapon.get("charge",1)
				mount = weapon["mount"]
				weapon["current_charge"] = min(charge,weapon.get("current_charge",0)+1)
				if weapon.get("ammo") == 0: continue
				if weapon["current_charge"] != charge:
					for i in range(amount):
						query.log(a,weapon["name"]+str(i)+" charging...")
					continue
				else:
					weapon["current_charge"] = 0
				for i in range(amount):
					if weapon.get("ammo") == 0: continue
					action = " firing!"
					if pship.get("subtype") == "missile":
						action = " seeking!"
					msg = weapon["name"] + str(i) + action
					query.log(a,msg,weapon=weapon["name"])
					targets = query.targets(weapon,possible_targets,main_target)
					for target in targets:
						chance = query.hit_chance(pship["ship"],target,weapon)
						msg = "Target: "+target["name"]+ "(hit chance: "+str(round(chance*100)/100)+")"
						query.log(a,msg,target=target["name"],hit_chance=chance)
						for j in range(shots):
							if weapon["type"] != "missile" and weapon["type"] != "drone":
								roll = random.random()
								if chance > roll:
									do_damage(pship["ship"],target,weapon["damage"],a)
									if weapon.get("self-destruct"):
										pship["ship"]["stats"]["hull"]["current"] = 0
								else:
									miss(pship["ship"],target,a)
							else:
								if weapon["ammo"] > 0:
									launch_drone_missile(pship,target,weapon,a)
									weapon["ammo"] -= 1
def decay_drones_missiles(a):
	decayed = []
	for name,pship in a["drones/missiles"].items():
		if pship.get("duration") is not None:
			pship["duration"] -= 1
			if pship["duration"] < 1:
				decayed.append(name)
	for name in decayed:
		query.get_combat_ship(a,a["drones/missiles"][name]["source"])["drones/missiles"].remove(name)
		del a["drones/missiles"][name]
def update_active_ships(a):
	removed = []
	for pship in a["combat_ships"].values():
		if pship["ship"]["stats"]["hull"]["current"] < 1:
			removed.append(pship)
	for pship in removed:
		del a["combat_ships"][pship["name"]]
def do_damage(source,target,amount,a):
	remaining = amount
	data = []
	tstats = target.get("stats",target["ship"]["stats"])
	for vital in ["shield","armor","hull"]:
		if not remaining: break
		damage_entry = {
			"layer": vital
		}
		block = tstats[vital]["block"]
		block = min(remaining,block)
		if remaining and block:
			damage_entry["block"] = block
			remaining -= block
		soak = query.damage_soak(target,vital)
		soak = min(remaining,soak)
		if remaining and soak:
			damage_entry["soak"] = soak
			tstats[vital]["current"] -= current
			remaining -= soak
		current = tstats[vital]["current"]
		current = min(remaining,current)
		if remaining and current:
			damage_entry["damage"] = current
			tstats[vital]["current"] -= current
			remaining -= current
		data.append(damage_entry)
	if remaining:
		data.append({
			"layer": "overkill",
			"damage": remaining
		})
	msgs = []
	for damage_entry in data:
		msg = ""
		damage = damage_entry.get("damage")
		block = damage_entry.get("block")
		soak = damage_entry.get("soak")
		if damage: msg += str(damage) + " to "+ damage_entry["layer"]
		if block or soak:
			msg += "("
			if block:
				msg += str(block) + "blocked"
				if soak:
					msg += ","
			if soak:
				msg += str(soak) + "soaked"
			msg += ")"
		damage_entry["msg"] = msg
		msgs.append(msg)
	msg = "hit! " + ", ".join(msgs)
	query.log(a,msg,source=source["name"],target=target["name"],data=data)
def miss(source,target,a):
	msg = "miss."
	query.log(a,msg,source=source["name"],target=target["name"])
def launch_drone_missile(source,target,weapon,a):
	id = source.get("drones/missiles.count",0)+1
	source["drones/missiles.count"] = id
	name = source["name"]+","+weapon["name"]+","+str(id)
	if weapon["type"] == "missile":
		predef = defs.premade_ships["missile_hull"]
	else:
		predef = defs.premade_ships[weapon["ship_predef"]]
	pgear = predef["inventory"]["gear"]
	entry = {
		"id": id,
		"type": predef["ship"],
		"subtype": weapon["type"],
		"name": name,
		"source": source["name"],
		"target": target["name"],
		"inventory": {
			"gear": {} | pgear
		},
		"weapons": query.drone_missile_weapons(weapon),
		"ship": {
			"name": name,
			"type": predef["ship"],
			"inventory": {
				"items": {},
				"gear": {} | pgear
			}
		}
	}
	stats.update_ship(entry["ship"],save=False)
	source["drones/missiles"].append(entry["name"])
	a["drones/missiles"][name] = entry
	msg = source["name"] + " has launched the "+weapon["type"]+" "+name
	query.log(a,msg,name=name,source=source["name"],target=target["name"])
def win(a_ships,b_ships):
	winners = a_ships
	losers = b_ships
	items = {}
	for pship in losers.values():
		kill(pship,items)
	distribute_loot(winners,items)
def draw(battle):
	for a in battle["sides"]:
		for pship in a["ships"].values():
			kill(pship)
def retreat(battle,self):
	end_battle(battle)
	response.to_nav(self)
def kill(pship,items=None):
	if items is not None:
		for item in pship.get_gear().keys():
			if item in defs.weapons:
				stats = pship["stats"]
				stats["hull"]["current"] = 1
				stats["armor"]["current"] = 0
				stats["shield"]["current"] = stats["shield"]["max"]
				break
		if "loot" in pship:
			loot.generate(pship["loot"],items)
	map.remove_ship(pship)
	owner = pship["owner"]
	npc = defs.npc_characters.get(owner)
	if npc and "spawn" in npc:
		pship["pos"] = copy.deepcopy(npc["spawn"])
	else:
		pship["pos"] = copy.deepcopy(default_pos)
	map.add_ship2(pship)
def end_battle(battle):
	for a in battle["sides"]:
		for pship in a["ships"].values():
			del query.ship_battle[pship["name"]]
	query.battles.remove(battle)
def distribute_loot(winners,items):
	for pship in winners.values():
		inv = pship["inventory"]["items"]
		for item,amount in items.items():
			size = Item.size(item)
			space = pship.get_space()
			amount = min(amount,space//size)
			amount = max(amount,0)
			if not amount: continue
			inv.add(item,amount)
			items[item] -= amount
		pship.save()
	if len(items):
		pship = winners[list(winners.keys())[0]]
		pos = pship["pos"]
		omap = map.otiles(pos["system"])
		otile = omap.get(pos["x"],pos["y"])
		if "items" not in otile:
			otile["items"] = {}
		for item,amount in items.items():
			if not amount: continue
			if item not in otile["items"]:
				otile["items"][item] = 0
			otile["items"][item] += amount
		omap.set(pos["x"],pos["y"],otile)
		omap.save()