import copy,time

tag_to_ship = {}
def init():
	ai_tags = []
	ai_names = {}
	for spawner_name,data in defs.spawners.items():
		for predef_name,ship_names in data["ships"].items():
			for idx,ship_name in enumerate(ship_names):
				ai_tag = spawner_name+":"+predef_name+":"+str(idx)
				ai_tags.append(ai_tag)
				if not ship_name:
					predef = defs.premade_ships[predef_name]
					ship_name = predef["default_name"]
				ai_names[ai_tag] = ship_name
	for name,data in dict(defs.ships.items()).items():
		if "predef" in data and not "ai_tag" in data:
			data.delete()
			continue
		if "predef" in data:
			if data["ai_tag"] not in ai_tags:
				data.delete()
				continue
			tag_to_ship[data["ai_tag"]] = data
			if data["custom_name"] != ai_names[data["ai_tag"]]:
				data["custom_name"] = ai_names[data["ai_tag"]]
	tick()
def tick():
	for name,data in defs.spawners.items():
		for predef_name,ship_names in data["ships"].items():
			for idx,ship_name in enumerate(ship_names):
				pship = get_predef_ship(data,name,predef_name,ship_name,idx)
				if "respawn" in pship or "dead" in pship["props"]:
					if "respawn" in pship:
						if time.time() < pship["respawn"]:
							continue
						del pship["respawn"]
						del pship["props"]["dead"]
					else:
						pship["respawn"] = time.time()+data["respawn"]
						continue
					map.remove_ship(pship)
					pship["pos"] = copy.deepcopy(data["pos"])
					sstats = pship["stats"]
					sstats["hull"]["current"] = sstats["hull"]["max"]
					sstats["armor"]["current"] = sstats["armor"]["max"]
					sstats["shield"]["current"] = sstats["shield"]["max"]
					map.add_ship2(pship)
					pship.save()
def get_predef_ship(spawner,spawner_name,predef_name,ship_name,idx):
	ai_tag = spawner_name+":"+predef_name+":"+str(idx)
	if ai_tag in tag_to_ship:
		return tag_to_ship[ai_tag]
	predef = defs.premade_ships[predef_name]
	if not ship_name:
		ship_name = predef["default_name"]
	new_ship = ship.new(predef["ship"],spawner["owner"])
	new_ship["pos"] = copy.deepcopy(spawner["pos"])
	if "loot" in predef:
		new_ship["loot"] = predef["loot"]
	new_ship["predef"] = predef_name
	new_ship["custom_name"] = ship_name
	new_ship["ai_tag"] = ai_tag
	ditems = predef["inventory"]["items"]
	dgear = predef["inventory"]["gear"]
	for item,amount in ditems.items():
		new_ship["inventory"]["items"].add(item,amount)
	for item,amount in dgear.items():
		new_ship["inventory"]["gear"].add(item,amount)
	stats.update_ship(new_ship)
	map.add_ship2(new_ship)
	new_ship.save()
	tag_to_ship[ai_tag] = new_ship
	return new_ship

from . import defs,ship,map,stats