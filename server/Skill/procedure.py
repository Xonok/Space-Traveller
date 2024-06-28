import copy
from server import defs,error,ship
from . import query
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
			skill_cost += query.get_skill_cost(skill,level,True)
		data["skill_cost"] = skill_cost
		#print(name,skill_cost,skill_req)
	for name,cdata in defs.characters.items():
		update_skillpoints(cdata)
	#loop through characters, calculate skillpoints
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
	result = min(510,int(200*((target_level+1)/(self_level+1))**mod))
	new_xp = cdata["xp"] + result
	prev_level = cdata["level"]
	while new_xp >= 1000:
		new_xp -= 1000
		cdata["level"] += 1
	cdata["xp"] = new_xp
	level_diff = cdata["level"]-prev_level
	new_level = cdata["level"]
	xp_left = 1000-cdata["xp"]
	if level_diff:
		update_skillpoints(cdata)
	return result,xp_left,level_diff,new_level
def gain_xp_flat(cdata,amount):
	if cdata["name"] in defs.npc_characters: return
	if amount < 0: return
	if type(amount) != int: raise Exception("Amount must not be "+type(amount).__name__)
	new_xp = cdata["xp"] + amount
	prev_level = cdata["level"]
	while new_xp >= 1000:
		new_xp -= 1000
		cdata["level"] += 1
	cdata["xp"] = new_xp
	level_diff = cdata["level"]-prev_level
	if level_diff:
		update_skillpoints(cdata)
def update_skillpoints(cdata):
	if cdata["name"] in defs.npc_characters: return
	level = cdata["level"]
	skills = cdata["skills"]
	skillpoints_total = level*1 #Might be changed to *5 later
	skillpoints_used = 0
	for name,amount in skills.items():
		skillpoints_used += query.get_skill_cost(name,amount,cumulative=True)
	cdata["skillpoints"] = skillpoints_total-skillpoints_used
def train_skill(cdata,skill,tstruct):
	if not tstruct: raise error.User("There is no planet here to train skills on.")
	loc_data = query.get_location(tstruct["name"])
	current = cdata["skills"].get(skill,0)
	points = cdata["skillpoints"]
	pships = ship.character_ships(cdata["name"])
	if skill not in loc_data: raise error.User("The skill "+skill+" can't be trained here.")
	if current >= loc_data[skill]["max"]: raise error.User("This location can't train "+skill+" further.")
	cost = query.get_skill_cost(skill,current+1)
	if cost > points: raise error.User("Not enough skillpoints. Have "+str(current)+", but need "+str(cost))
	#TODO: credit cost
	item_req = copy.deepcopy(loc_data[skill].get("item_req"))
	if item_req:
		items = {}
		for item in item_req.keys():
			items[item] = 0
		for name,pship in pships.items():
			for item,amount in item_req.items():
				if item in items:
					items[item] += pship["inventory"]["items"].get(item)
		for item,amount in item_req.items():
			if items[item] < amount:
				raise error.User("Not enough "+defs.items[item]["name"]+", need "+str(amount))
		for name,pship in pships.items():
			for item,amount in item_req.items():
				available = pship["inventory"]["items"].get(item)
				delta = min(available,amount)
				pship["inventory"]["items"].add(item,-delta)
				item_req[item] -= delta
			pship.save()
	cdata["skillpoints"] -= cost
	cdata["skills"][skill] = current+1
	cdata.save()
	#not enough credits
	#item req missing