from server import defs

def get_location(struct_name):
	if struct_name not in defs.skill_locations: return
	loc_data = defs.skill_locations[struct_name]
	skill_data = {}
	for name in loc_data.keys():
		skill_data[name] = defs.skills[name]
	return loc_data,skill_data