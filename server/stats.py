def make_scale(max,block,soak,resist,reg):
	return {
		"max": max,
		"current": max,
		"block": block,
		"soak": soak,		#flat damage reduction
		"resist": resist,	#percent damage reduction
		"reg": reg
	}
def regenerate_armor(pship):
	regenerate(pship,"hull")
	regenerate(pship,"armor")
def regenerate(pship,stat_name):
	sgear = pship["inventory"]["gear"]
	stats = pship["stats"]
	total_reg = 0
	for item,amount in sgear.items():
		idata = defs.items[item]
		props = idata.get("props",{})
		reg = props.get(stat_name+"_reg")
		if reg:
			total_reg += reg*amount
	total_reg = min(total_reg,stats[stat_name]["max"]-stats[stat_name]["current"])
	stats[stat_name]["current"] += total_reg
	return total_reg
def update_ship(pship,save=True):
	ship_type = pship.get("ship",pship["type"])
	shipdef = defs.ship_types[ship_type]
	cdata = defs.characters[pship["owner"]]
	skills = cdata.get("skills",{})
	command_used = cdata.get("command_used",0)
	command_max = cdata.get("command_max",0)
	if pship["owner"] in defs.npc_characters:
		command_factor = 1
	elif command_used == 0:
		command_factor = 1
	elif command_max == 0:
		if command_used > 0:
			command_factor = 0.2
		else:
			command_factor = 1
	else:
		command_factor = max(command_max/command_used,0.2)
	piloting = skills.get("piloting",0)
	defense = skills.get("defense",0)
	piloting_deficit = shipdef["tech"]-piloting
	piloting_factor = 1
	if piloting_deficit > 0:
		piloting_factor = max(0.5**piloting_deficit,0.2)
	if cdata["name"] in defs.npc_characters:
		piloting_factor = 1
	prev = {}
	if "stats" in pship:
		prev = pship["stats"]
		pship["stats"]["hull"]["block"] = pship["stats"]["hull"].get("block",0)
		pship["stats"]["armor"]["block"] = pship["stats"]["armor"].get("block",0)
		pship["stats"]["shield"]["block"] = pship["stats"]["shield"].get("block",0)
	shipdef = defs.ship_types[Item.ship_type(pship)]
	default = {
		"hull": make_scale(shipdef["hull"],0,0,0,0),
		"armor": make_scale(0,0,0,0,0),
		"shield": make_scale(0,0,0,0,0)
	}
	pship["stats"] = default | prev
	stats = pship["stats"]
	prev_armor_max = stats["armor"]["max"]
	pship["stats"]["hull"]["max"] = shipdef["hull"]
	if pship["stats"]["hull"]["current"] < 0:
		pship["stats"]["hull"]["current"] = 0
	stats["armor"]["max"] = 0
	stats["armor"]["soak"] = 0	
	stats["armor"]["reg"] = 0
	stats["shield"]["max"] = 0
	stats["shield"]["reg"] = 0
	hull_factor = stats["hull"]["current"]/stats["hull"]["max"]/2
	stats["speed"] = int(shipdef["speed"]*(0.25+hull_factor*1.5))
	stats["agility"] = int(shipdef["agility"]*(0.5+hull_factor))
	stats["tracking"] = shipdef.get("tracking",0)
	stats["size"] = shipdef["size"]
	stats["weight"] = shipdef["size"]
	stats["stealth"] = 0
	stats["command_factor"] = float(command_factor)
	stats["piloting_factor"] = float(piloting_factor)
	for item,amount in pship["inventory"]["gear"].items():
		idata = defs.items[item]
		tech = idata.get("tech",0)
		item_category = defs.item_categories[idata["type"]]
		skill = item_category.get("skill")
		skill_factor = 1
		if skill:
			skill_lvl = skills.get(skill,0)
			skill_deficit = tech-skill_lvl
			if skill_deficit > 0:
				skill_factor = max(0.5**skill_deficit,0.2)
		if cdata["name"] in defs.npc_characters:
			skill_factor = 1
		props = idata.get("props",{})
		if "armor_max" in props:
			stats["armor"]["max"] += int(amount*props["armor_max"]*skill_factor)
		if "armor_soak" in props:
			stats["armor"]["soak"] += int(amount*props["armor_soak"]*skill_factor)
		if "armor_reg" in props:
			stats["armor"]["reg"] += int(amount*props["armor_reg"]*skill_factor)
		if "shield_max" in props:
			stats["shield"]["max"] += int(amount*props["shield_max"]*skill_factor)
		if "shield_reg" in props:
			stats["shield"]["reg"] += int(amount*props["shield_reg"]*skill_factor)
		if "weight" in props:
			stats["weight"] += amount*props["weight"]
		if "stealth" in props:
			stats["stealth"] += int(amount*props["stealth"]*skill_factor)
		if "aura_speed_penalty" in props:
			stats["speed"] *= props["aura_speed_penalty"]
		if "aura_speed_bonus" in props:
			stats["speed"] *= 1+props["aura_speed_bonus"]*skill_factor
		if "aura_agility_penalty" in props:
			stats["agility"] *= props["aura_agility_penalty"]
		if "aura_tracking_penalty" in props:
			stats["tracking"] *= props["aura_tracking_penalty"]
	stats["agility"] = round(stats["agility"] * stats["size"]/stats["weight"]*command_factor*piloting_factor)
	stats["tracking"] = round(stats["tracking"]*command_factor*piloting_factor)
	stats["speed"] = round(stats["speed"]*command_factor*piloting_factor)
	if stats["armor"]["max"] > prev_armor_max:
		stats["armor"]["current"] += stats["armor"]["max"]-prev_armor_max
	if stats["armor"]["current"] > stats["armor"]["max"]:
		stats["armor"]["current"] = stats["armor"]["max"]
	if stats["shield"]["current"] > stats["shield"]["max"]:
		stats["shield"]["current"] = stats["shield"]["max"]
	if not Battle.ship_battle(pship):
		stats["shield"]["current"] = stats["shield"]["max"]
	stats["threat"] = threat.calculate(pship)
	if save:
		pship.save()
from . import defs,Battle,Item,threat