import copy,time

name_to_ship = {}
def init():
	for name,data in defs.ships.items():
		if "predef" in data:
			name_to_ship[data["custom_name"]] = data
	tick()
def tick():
	for name,data in defs.spawners.items():
		for predef_name,ship_names in data["ships"].items():
			for ship_name in ship_names:
				pship = get_predef_ship(data,predef_name,ship_name)
				if "respawn" in pship or not map.pos_equal(pship["pos"],data["pos"]):
					if "respawn" in pship:
						if time.time() < pship["respawn"]:
							continue
						del pship["respawn"]
					else:
						pship["respawn"] = time.time()+data["respawn"]
						continue
					map.remove_ship(pship)
					pship["pos"] = copy.deepcopy(data["pos"])
					stats = pship["stats"]
					stats["hull"]["current"] = stats["hull"]["max"]
					stats["armor"]["current"] = stats["shield"]["max"]
					stats["shield"]["current"] = stats["shield"]["max"]
					map.add_ship2(pship)
					pship.save()
def get_predef_ship(spawner,predef_name,ship_name):
	if ship_name in name_to_ship:
		return name_to_ship[ship_name]
	predef = defs.premade_ships[predef_name]
	new_ship = ship.new(predef["ship"],spawner["owner"])
	new_ship["pos"] = copy.deepcopy(spawner["pos"])
	new_ship["loot"] = predef["loot"]
	new_ship["predef"] = predef_name
	new_ship["custom_name"] = ship_name
	ditems = predef["inventory"]["items"]
	dgear = predef["inventory"]["gear"]
	for item,amount in ditems.items():
		new_ship["inventory"]["items"].add(item,amount)
	for item,amount in dgear.items():
		new_ship["inventory"]["gear"].add(item,amount)
	stats.update_ship(new_ship)
	map.add_ship2(new_ship)
	new_ship.save()
	name_to_ship[ship_name] = new_ship
	return new_ship

from . import defs,ship,map,stats