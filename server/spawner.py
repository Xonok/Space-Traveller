import copy,time

tag_to_ship = {}
def init():
	for name,data in dict(defs.ships.items()).items():
		if "predef" in data and not "ai_tag" in data:
			data.delete()
			continue
		if "predef" in data:
			tag_to_ship[data["ai_tag"]] = data
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
def get_predef_ship(spawner,spawner_name,predef_name,ship_name):
	if ":" not in ship_name:
		raise Exception("Invalid ship name in spawner "+spawner_name+": format needs to be ai_tag:custom_name.")
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