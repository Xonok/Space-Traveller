from . import defs

standard_cost = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
standard_cost_cum = [0,1,3,6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,190,210]
def init():
	for name,data in defs.premade_ships.items():
		ship_def = defs.ship_types[data["ship"]]
		gear = data["inventory"]["gear"]
		skill_req = {
			"piloting": ship_def["tech"]
		}
		items = []
		for item in gear.keys():
			items.append(item)
		for item in items:
			idata = defs.items[item]
			item_category = defs.item_categories[idata["type"]]
			skill = item_category.get("skill")
			if skill:
				skill_req[skill] = max(skill_req.get(skill,0),idata["tech"])
		skill_cost = 0
		for skill,level in skill_req.items():
			skill_cost += get_skill_cost(skill,level)
		data["skill_cost"] = skill_cost
		print(name,skill_cost,skill_req)
def get_skill_cost(skill,level):	
	skill_def = defs.skills[skill]
	formula = skill_def["formula"]
	if formula == "standard":
		return standard_cost_cum[level]
	else:
		raise Exception("Unknown skill cost formula: "+formula)
def gain_xp(cdata,target):
	if target["owner"] not in defs.npc_characters: return
	predef_name = target.get("predef")
	if not predef_name: return
	predef = defs.premade_ships[predef_name]
	self_level = cdata["level"]
	target_level = predef["skill_cost"]
	if self_level < target_level:
		mod = 2 if self_level < 10 else 5
	else:
		mod = 0.9
	result = min(510,int(50*((target_level+1)/(self_level+1))**mod))
	new_xp = cdata["xp"] + result
	prev_level = cdata["level"]
	while new_xp >= 1000:
		new_xp -= 1000
		cdata["level"] += 1
	cdata["xp"] = new_xp
	level_diff = cdata["level"]-prev_level
	new_level = cdata["level"]
	xp_left = 1000-cdata["xp"]
	return result,xp_left,level_diff,new_level