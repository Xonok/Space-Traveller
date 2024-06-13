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