from server import defs

def get_location(struct_name):
	if struct_name not in defs.skill_locations: return
	loc_data = defs.skill_locations[struct_name]
	return loc_data
def get_skill_data(loc_data):
	skill_data = {}
	for name in loc_data.keys():
		skill_data[name] = defs.skills[name]
	return skill_data
standard_cost = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
standard_cost_cum = [0,1,3,6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,190,210]
def get_skill_cost(skill,level,cumulative=False):	
	skill_def = defs.skills[skill]
	formula = skill_def["formula"]
	if formula == "standard":
		if cumulative:
			return standard_cost_cum[level]
		else:
			return standard_cost[level]
	else:
		raise Exception("Unknown skill cost formula: "+formula)
def check(cdata,skill,amount):
	return cdata["skills"].get(skill,0) >= amount
def command_factor_battle(pship):
	cdata = defs.characters[pship["owner"]]
	skills = cdata.get("skills",{})
	command_battle_used = cdata.get("command_battle_used",0)
	command_max = cdata.get("command_max",0)
	if pship["owner"] in defs.npc_characters:
		command_factor_battle = 1
	elif command_battle_used == 0:
		command_factor_battle = 1
	elif command_max == 0:
		if command_battle_used > 0:
			command_factor_battle = 0.2
		else:
			command_factor_battle = 1
	else:
		command_factor_battle = max(command_max/command_battle_used,0.2)
		command_factor_battle = min(command_factor_battle,1)
	return command_factor_battle
def command_factor_freight(pship):
	cdata = defs.characters[pship["owner"]]
	skills = cdata.get("skills",{})
	command_freight_used = cdata.get("command_freight_used",0)
	command_max = cdata.get("command_max",0)
	command_freight_bonus = cdata.get("command_freight_bonus",0)
	command_max_freight = command_max+command_freight_bonus
	if pship["owner"] in defs.npc_characters:
		command_factor_freight = 1
	elif command_freight_used == 0:
		command_factor_freight = 1
	elif command_max_freight == 0:
		if command_freight_used > 0:
			command_factor_freight = 0.2
		else:
			command_factor_freight = 1
	else:
		command_factor_freight = max(command_max_freight/command_freight_used,0.2)
		command_factor_freight = min(command_factor_freight,1)
	return command_factor_freight
def skill_factor(cdata,item,):
	skills = cdata.get("skills",{})
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
	return skill_factor