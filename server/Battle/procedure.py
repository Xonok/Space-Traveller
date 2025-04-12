import random,copy
from server import stats,error,ship,defs,loot,Item,map,Name,character,quest,Skill,exploration,func
from . import query,response

default_pos = {
	"x": -2,
	"y": 2,
	"rotation": 0,
	"system": "Megrez"
}

def start_battle(cdata,target_name,self):
	if not target_name: raise error.User("No target for attack.")
	if cdata["name"] not in defs.npc_characters and ship.get(target_name)["owner"] not in defs.npc_characters:
		raise error.User("Can't attack player characters.")
	self_name = cdata["name"]
	pos = query.get_combat_pos(self_name)
	attackers = query.get_ships(self_name,pos)
	defenders = query.get_ships(ship.get(target_name)["owner"],pos)
	attackers_active = query.get_combat_ships(attackers)
	defenders_active = query.get_combat_ships(defenders)
	if not len(attackers): raise error.User("You don't have any ships here. Weird.")
	if not len(defenders): raise error.User("The ship you're trying to attack isn't here (anymore).")
	if not len(attackers_active): raise error.User("None of your ships can currently fight. Check that they have weapons equipped and hull points remaining.")
	for name in attackers.keys():
		if name in query.ship_battle:
			raise error.User("You are already in a battle.")
	for name in defenders.keys():
		if name in query.ship_battle:
			raise error.User("They are already in a battle.")
	if not len(defenders_active):
		response.message(self,"The defending forces immediately crumble.")
		win(attackers,defenders)
		return
	battle = query.in_combat([attackers,attackers_active],[defenders,defenders_active])
	for pship in attackers.values():
		stats.update_ship(pship)
	for pship in defenders.values():
		stats.update_ship(pship)
	for side in battle["sides"]:
		update_order(side)
	response.to_battle(self)
def attack(cdata):
	battle = query.get_battle(cdata)
	rounds = len(battle["sides"][0]["logs"])
	if not battle: raise error.User("Your active ship isn't in any battles currently.")
	do_round(battle)
	return query.get_battle_update(battle,rounds)
def do_round(battle,force=None):
	a = battle["sides"][0]
	b = battle["sides"][1]
	a["logs"].append([])
	b["logs"].append([])
	if force:
		a["logs"][-1].append({"msg":"Couldn't retreat. Combat continues."})
		b["logs"][-1].append({"msg":"Pursuing fleeing enemies. Combat continues."})
	rounds = len(a["logs"])
	ships_a = a["combat_ships"]
	ships_b = b["combat_ships"]
	order_a = a["order"]
	order_b = b["order"]
	drones_missiles_a = a["drones/missiles"]
	drones_missiles_b = b["drones/missiles"]
	regenerate_shields(a,ships_a,drones_missiles_a)
	regenerate_shields(b,ships_b,drones_missiles_b)
	point_defense(a,b,drones_missiles_a,ships_a)
	point_defense(b,a,drones_missiles_b,ships_b)
	kill_drones_missiles(a)
	kill_drones_missiles(b)
	new_drones_a = ships_fire(a,b,rounds,drones_missiles_a,order_a)
	new_drones_b = ships_fire(b,a,rounds,drones_missiles_b,order_b)
	for name, entry in new_drones_a:
		a["combat_ships"][name] = entry
	for name, entry in new_drones_b:
		b["combat_ships"][name] = entry
	kill_drones_missiles(a,False)
	kill_drones_missiles(b,False)
	decay_drones_missiles(a)
	decay_drones_missiles(b)
	char_a = None
	char_b = None
	for name in a["ships"]:
		char_a = defs.characters[defs.ships[name]["owner"]]
	for name in b["ships"]:
		char_b = defs.characters[defs.ships[name]["owner"]]
	update_active_ships(a,char_b,b)
	update_active_ships(b,char_a,a)
	a_count = len(a["combat_ships"])
	b_count = len(b["combat_ships"])
	if not a_count and not b_count:
		draw(battle)
		end_battle(battle)
	elif a_count and not b_count:
		win(a["ships"],b["ships"],battle,a)
		end_battle(battle)
	elif b_count and not a_count:
		win(b["ships"],a["ships"],battle,b)
		end_battle(battle)
	for pship in a["ships"].values():
		stats.update_ship(pship)
	for pship in b["ships"].values():
		stats.update_ship(pship)
	for side in battle["sides"]:
		update_order(side)
	battle["round"] += 1
def regenerate_shields(a,*lists):
	for names in lists:
		for pship in names.values():
			amount = stats.regenerate(pship["ship"],"shield")
			if amount:
				msg = query.name(pship)+" regenerated "+str(amount)+" points of shields."
				query.log(a,msg,shield_reg=amount)
def point_defense(a,b,*shooterses):
	targets = b["drones/missiles"]
	if not len(targets): return
	for shooters in shooterses:
		for idx,pship in enumerate(shooters.values()):
			can_pd = False
			for weapon in pship["weapons"].values():
				if weapon.get("shots_pd"):
					can_pd = True
					break
			if can_pd:
				query.log(a,query.name(pship)+" point defense: ")
				for name,weapon in pship["weapons"].items():
					shots_pd = weapon.get("shots_pd",0)
					if shots_pd:
						action = " firing!"
						msg = weapon["name"] + action
						query.log(a,"\t"+msg,weapon=weapon["name"])
						for i in range(weapon["amount"]*shots_pd):
							target = random.choice(list(targets.values()))
							chance = query.hit_chance(pship["ship"],target,weapon)
							msg = "Target: "+query.name(target)+ " (hit chance: "+str(round(chance*100)/100)+")"
							query.log(a,"\t\t"+msg,target=target["name"],hit_chance=chance)
							roll = random.random()
							if chance > roll:
								do_damage(pship["ship"],target,weapon,a)
							else:
								miss(pship["ship"],target,a)
				if idx < len(shooters)-1:
					query.log(a,"\n")
def kill_drones_missiles(a,do_log=True):
	dead = []
	for name,target in a["drones/missiles"].items():
		if target["ship"]["stats"]["hull"]["current"] < 1:
			msg = target["subtype"]+" "+query.name(target)+" destroyed"
			if do_log:
				query.log(a,msg,type=target["subtype"],destroyed=query.name(target))
			host = a["combat_ships"].get(target["source"])
			if host:
				host["drones/missiles"].remove(target["name"])
			dead.append(name)
	for name in dead:
		del a["drones/missiles"][name]
def ships_fire(a,b,rounds,*shooterses):
	possible_targets = b["combat_ships"]
	new_drones = []
	for shooters in shooterses:
		for idx,pship in enumerate(shooters):
			if pship.get("subtype") == "missile": continue
			query.log(a,query.name(pship)+" attacking: ")
			main_target = query.get_main_target(possible_targets)
			if "target" in pship:
				if pship["target"] in possible_targets:
					main_target = possible_targets[pship["target"]]
			if len(pship["drones/missiles"]):
				query.log(a,"\tGuiding missiles...")
			for name in pship["drones/missiles"]:
				data = a["drones/missiles"][name]
				if data.get("subtype") != "missile": continue
				weapon = data["weapons"]["payload"]
				main_target = random.choice(list(possible_targets.values()))
				if "target" in data:
					if data["target"] in possible_targets:
						main_target = possible_targets[data["target"]]
				targets = query.targets(weapon,possible_targets,main_target)
				for target in targets:
					evade = query.evade_chance(pship["ship"],target,weapon,rounds)
					chance = query.hit_chance(data["ship"],target,weapon)
					roll = random.random()
					msg = "\t\t"+data["wep_name"]+","+str(data["ship"]["id"])+" targeting "+query.name(target)+" (hit: "+str(round(chance*100)/100)
					if evade:
						msg += ", evade: "+str(round(evade*100)/100)
					query.log(a,msg+")")
					roll = random.random()
					if evade > roll:
						query.log(a,"\t\t"+"Failed to lock on target.",target=query.name(target["ship"]),hit_chance=chance)
						continue
					if chance > roll:
						do_damage(data["ship"],target,weapon,a)
						data["ship"]["stats"]["hull"]["current"] = 0
					else:
						miss(data["ship"],target,a)
			for name,weapon in pship["weapons"].items():
				shots = weapon["shots"]
				amount = weapon["amount"]
				charge = weapon.get("charge",1)
				weapon["current_charge"] = min(charge,weapon.get("current_charge",0)+1)
				wtype = weapon.get("type")
				if weapon.get("ammo") == 0 and wtype != "drone": 
					query.log(a,"\t"+weapon["name"]+" out of ammo.")
					continue
				if weapon["current_charge"] != charge:
					query.log(a,"\t"+weapon["name"]+" charging...")
					continue
				else:
					weapon["current_charge"] = 0
					if name != "payload":
						if pship.get("subtype") == "missile":
							msg = weapon["name"]+" seeking!"
						elif wtype == "missile":
							msg = "Launching "+weapon["name"]+" missiles"
						elif wtype == "drone":
							msg = "Launching "+weapon["name"]+" drone"
						else:
							msg = weapon["name"]+" firing!"
						if weapon.get("ammo") != 0:
							query.log(a,"\t"+msg,weapon=weapon["name"])
				for i in range(amount):
					if weapon.get("ammo") == 0: continue
					targets = query.targets(weapon,possible_targets,main_target)
					for target in targets:
						evade = query.evade_chance(pship["ship"],target,weapon,rounds)
						if wtype == "drone":
							evade = 0
						chance = query.hit_chance(pship["ship"],target,weapon)
						msg = "Target: "+query.name(target["ship"])
						if wtype != "missile" and wtype != "drone":
							msg += " (hit: "+str(round(chance*100)/100)
						if evade:
							msg += ", evade: "+str(round(evade*100)/100)
						query.log(a,"\t\t"+msg+")",target=query.name(target["ship"]),hit_chance=chance)
						roll = random.random()
						if evade > roll:
							query.log(a,"\t\t\t"+"Failed to lock on target.",target=query.name(target["ship"]),hit_chance=chance)
							continue
						for j in range(shots):
							if wtype != "missile" and wtype != "drone":
								roll = random.random()
								if chance > roll:
									do_damage(pship["ship"],target,weapon,a)
									if weapon.get("self-destruct"):
										pship["ship"]["stats"]["hull"]["current"] = 0
								else:
									miss(pship["ship"],target,a)
							else:
								if weapon["ammo"] > 0:
									new_drone = launch_drone_missile(pship,target,weapon,a)
									if new_drone:
										new_drones.append(new_drone)
									weapon["ammo"] -= 1
			if idx < len(shooters)-1:
				query.log(a,"\n")
	return new_drones
def decay_drones_missiles(a):
	decayed = []
	for name,pship in a["drones/missiles"].items():
		if pship.get("duration") is not None:
			pship["duration"] -= 1
			if pship["duration"] < 0:
				decayed.append(name)
	for name in decayed:
		host = a["combat_ships"].get(a["drones/missiles"][name]["source"])
		if host:
			host["drones/missiles"].remove(name)
		del a["drones/missiles"][name]
def update_active_ships(a,cdata,b):
	removed = []
	for pship in a["combat_ships"].values():
		if pship["ship"]["stats"]["hull"]["current"] < 1:
			removed.append(pship)
			continue
	for pship in removed:
		del a["combat_ships"][pship["name"]]
		if cdata["name"] not in defs.npc_characters:
			results = Skill.gain_xp(cdata,pship["ship"])
			if not results: continue
			(xp_gain,xp_left,level_diff,new_level) = results
			if xp_gain:
				query.log(b,"Gained "+str(xp_gain)+" xp. ")
			if level_diff:
				query.log(b,"Leveled up. Now level "+str(new_level))
			if xp_gain:
				query.log(b,str(xp_left)+" until next level.")
			exploration.register_kill(cdata,pship["ship"])
def update_order(side):
	combat_ships = side["combat_ships"]
	order = []
	for name,ship in combat_ships.items():
		order.append(ship)
	def sorter(ship):
		return ship["ship"]["stats"]["initiative"]
	order.sort(reverse=True,key=sorter)
	side["order"] = order
def do_damage(source,target,weapon,a):
	remaining = weapon["damage"]
	anti_shield = weapon.get("damage_shield",0)
	anti_armor = weapon.get("damage_armor",0)
	anti_hull = weapon.get("damage_hull",0)
	data = []
	tstats = target.get("stats",target["ship"]["stats"])
	deflect = tstats.get("deflect",0)
	size = tstats["size"]
	for vital in ["shield","armor","hull"]:
		if not remaining: break
		damage_entry = {
			"layer": vital
		}
		prev_damage = remaining
		block = tstats[vital]["block"]
		block = min(remaining,block)
		if vital == "shield":
			remaining += anti_shield+1
		if vital == "armor":
			remaining += anti_armor
		if vital == "hull":
			remaining += anti_hull
		if remaining and block:
			damage_entry["block"] = block
			remaining -= block
		if remaining:
			if tstats[vital]["soak"]:
				current = tstats[vital]["current"]
				soak = query.damage_soak(target,vital)
				soak = min(current,remaining,soak+anti_armor)
				damage_entry["soak"] = soak
				tstats[vital]["current"] -= soak
				remaining -= soak
			else:
				dam_to_size = remaining/(remaining+size)
				def_to_size = deflect/(deflect+size)
				deflect_factor = (1-dam_to_size*def_to_size)**5
				current = tstats[vital]["current"]
				with_deflect = int(current/deflect_factor)
				current = min(remaining,current)
				if vital == "shield":
					current = min(remaining,with_deflect)
				deflect_amount = func.f2ir(current-current*deflect_factor)
				if vital == "shield" and deflect_amount:
					current -= deflect_amount
					remaining -= deflect_amount
					damage_entry["deflect_factor"] = deflect_factor
					damage_entry["deflect_amount"] = deflect_amount
				if current:
					damage_entry["damage"] = current
					tstats[vital]["current"] -= current
					remaining -= current
					remaining = max(remaining,0)
			remaining = min(prev_damage,remaining)
		if len(damage_entry) > 1:
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
		deflect_amount = damage_entry.get("deflect_amount")
		
		if damage: msg += str(damage) + " to "+ damage_entry["layer"]
		if deflect_amount: msg += " (" + str(deflect_amount) + " deflected)"
		if soak: msg += str(soak) + " to "+ damage_entry["layer"]
		if block:
			msg += "("
			msg += str(block) + "blocked"
			msg += ")"
		damage_entry["msg"] = msg
		msgs.append(msg)
	msg = "hit! " + ", ".join(msgs)
	query.log(a,"\t\t\t"+msg,source=query.name(source),target=query.name(target),data=data)
def miss(source,target,a):
	msg = "miss."
	query.log(a,"\t\t\t"+msg,source=source["name"],target=target["name"])
def launch_drone_missile(source,target,weapon,a):
	cdata = defs.characters[source["ship"]["owner"]]
	id = a["missiles.count"]+1
	a["missiles.count"] = id
	name = source["name"] + "," + weapon["name"]+ "," +str(id)
	custom_name = weapon["name"]+","+str(id)
	if weapon["type"] == "missile":
		if "ship_predef" in weapon:
			predef = defs.predefined_ships[weapon["ship_predef"]]
		else:
			predef = defs.predefined_ships["missile_hull"]
	else:
		predef = defs.predefined_ships[weapon["ship_predef"]]
	pgear = predef["gear"]
	display_name = weapon["name"]
	if "default_name" in predef and weapon["type"] != "missile":
		display_name = predef["default_name"]
	entry = {
		"id": id,
		"type": predef["ship"],
		"subtype": weapon["type"],
		"wep_name": weapon["name"],
		"name": name,
		"custom_name": display_name,
		"source": source["name"],
		"target": target["name"],
		"gear": {} | pgear,
		"weapons": query.drone_missile_weapons(weapon,cdata),
		"drones/missiles": [],
		"ship": {
			"id": id,
			"name": name,
			"custom_name": display_name,
			"source": source["name"],
			"type": predef["ship"],
			"owner": source["ship"]["owner"],
			"gear": {} | pgear,
			"wep_id": weapon["id"]
		}
	}
	if "payload" in entry["weapons"]:
		entry["duration"] = entry["weapons"]["payload"]["duration"]
	stats.update_ship(entry["ship"],save=False)
	msg = weapon["type"]+" launched."
	query.log(a,"\t\t\t"+msg,name=name,source=query.name(source["ship"]),target=query.name(target))
	if weapon["type"] == "missile":
		source["drones/missiles"].append(name)
		a["drones/missiles"][name] = entry
	else:
		return name,entry
def win(a_ships,b_ships,battle=None,winning_side=None):
	winners = a_ships
	losers = b_ships
	items = {}
	cdata = character.data(list(winners.values())[0]["owner"])
	bounty = 0
	for pship in losers.values():
		bounty += kill(pship,items=items,cdata=cdata)
	if battle:
		for side in battle["sides"]:
			side["logs"].append([])
			if side == winning_side:
				msg = "Bounty gained: "+str(bounty)
				query.log(side,msg,bounty=bounty)
				msg = "Loot gained:"
				for item,amount in items.items():
					msg += "\n\t"+str(amount)+" "+defs.items[item]["name"]
				query.log(side,msg,items=copy.deepcopy(items))
	distribute_loot(cdata,items,winning_side)
def draw(battle):
	for a in battle["sides"]:
		for pship in a["ships"].values():
			kill(pship)
def retreat(battle,side,self=None):
	chance = battle["sides"][side]["retreat_chance"]
	if random.random()<chance:
		end_battle(battle)
		if self:
			response.to_nav(self)
	else:
		do_round(battle,force=1)
		return query.get_battle_update(battle)
def kill(pship,items=None,cdata=None):
	bounty = 0
	if cdata:
		predef = defs.predefined_ships.get(pship.get("predef"),{})
		quest.update_targets_killed(cdata,predef)
		cdata["credits"] += predef.get("bounty",0)
		bounty += predef.get("bounty",0)
	if items is not None:
		for item in pship.get_gear().keys():
			if item in defs.weapons:
				pship["props"]["dead"] = True
				break
		if "loot" in pship:
			loot.generate(pship["loot"],items)
	map.remove_ship(pship)
	owner = pship["owner"]
	cdata = defs.characters[owner]
	npc = defs.npc_characters.get(owner)
	if npc and "spawn" in npc:
		pship["pos"] = copy.deepcopy(npc["spawn"])
	else:
		home_structure = defs.predefined_structures[cdata["home"]]
		home_pos = copy.deepcopy(home_structure["pos"])
		pship["pos"] = home_pos
	map.add_ship2(pship)
	cdata.save()
	return bounty
def end_battle(battle):
	for a in battle["sides"]:
		for pship in a["ships"].values():
			del query.ship_battle[pship["name"]]
			stats.update_ship(pship)
	query.battles.remove(battle)
def distribute_loot(cdata,items,winning_side):
	for item,amount in items.items():
		isize = Item.size(item)
		room = cdata.get_room()
		if isize:
			amount = min(amount,room//isize)
		amount = max(amount,0)
		if not amount: continue
		cdata["items"].add(item,amount)
		items[item] -= amount
	cdata.save()
	total = 0
	for amount in items.values():
		total += amount
	if total:
		msg = "Not enough space. Some loot was dropped."
		query.log(winning_side,msg)
		pship = ship.get(cdata["ships"][0])
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