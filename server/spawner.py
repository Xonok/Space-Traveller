import copy,time,random

tag_to_ship = {}
def init():
	ai_tags = []
	ai_tags_old = {}
	ai_names = {}
	for spawner_name,data in defs.spawners.items():
		reqs = data.get("reqs",{})
		max_spawns = reqs.get("max",1)
		for i in range(max_spawns):
			for predef_name,ship_names in data["ships"].items():
				for idx,ship_name in enumerate(ship_names):
					ai_tag = spawner_name+":"+predef_name+":"+str(i)+":"+str(idx)
					ai_tag_old = spawner_name+":"+predef_name+":"+str(idx)
					ai_tags.append(ai_tag)
					ai_tags_old[ai_tag_old] = ai_tag
					if not ship_name:
						predef = defs.premade_ships[predef_name]
						ship_name = predef["default_name"]
					ai_names[ai_tag] = ship_name
	for name,data in dict(defs.ships.items()).items():
		if "predef" in data and not "ai_tag" in data:
			data.delete()
			continue
		if "predef" in data:
			if data["ai_tag"] in ai_tags_old:
				data["ai_tag"] = ai_tags_old[data["ai_tag"]]
			if data["ai_tag"] not in ai_tags:
				data.delete()
				continue
			tag_to_ship[data["ai_tag"]] = data
			if data["custom_name"] != ai_names[data["ai_tag"]]:
				data["custom_name"] = ai_names[data["ai_tag"]]
	tick()
def tick():
	for spawner_name,data in defs.spawners.items():
		reqs = data.get("reqs",{})
		max_spawns = reqs.get("max",1)
		for i in range(max_spawns):
			ai_tags = {}
			for predef_name,ship_names in data["ships"].items():
				for idx,ship_name in enumerate(ship_names):
					ai_tag = spawner_name+":"+predef_name+":"+str(i)+":"+str(idx)
					ai_tags[ai_tag] = {
						"predef_name": predef_name,
						"idx": idx,
						"ship_name": ship_name
					}
			pos = data.get("pos")
			#if any ships alive, use their pos
			for ai_tag in ai_tags.keys():
				pship = get_predef_ship(ai_tag)
				if pship:
					pos = pship["pos"]
			#if not, generate a random pos
			if not pos:
				#required
				system = reqs.get("system")
				if not system: raise Exception("Spawner "+spawner_name+" doesn't have 'pos', so it must have reqs['system']")
				#optional
				tile_options = reqs.get("tile")
				no_ships = reqs.get("no_ships")
				near = reqs.get("near")
				pos = get_random_pos(system,tile_options,no_ships,near)
				#reqs must contain: system, could contain tile, no ships
			for ai_tag,data2 in ai_tags.items():
				predef_name = data2["predef_name"]
				idx = data2["idx"]
				ship_name = data2["ship_name"]
				#try finding the ship
				pship = get_predef_ship(ai_tag)
				if pship:
					#respawn if necessary
					if "respawn" in pship or "dead" in pship["props"]:
						if "respawn" in pship:
							if time.time() < pship["respawn"]:
								continue
							del pship["respawn"]
							del pship["props"]["dead"]
						else:
							pship["respawn"] = time.time()+data["respawn"]
							continue
						if not pos: continue #can't respawn because no valid location was found
						print(pos)
						map.remove_ship(pship)
						pship["pos"] = copy.deepcopy(pos)
						sstats = pship["stats"]
						sstats["hull"]["current"] = sstats["hull"]["max"]
						sstats["armor"]["current"] = sstats["armor"]["max"]
						sstats["shield"]["current"] = sstats["shield"]["max"]
						map.add_ship2(pship)
						pship.save()
						continue
				else:
					#if no ship, spawn a new one
					new_predef_ship(ai_tag,data,predef_name,ship_name,pos)
				
def get_predef_ship(ai_tag):
	if ai_tag in tag_to_ship:
		return tag_to_ship[ai_tag]
def new_predef_ship(ai_tag,spawner,predef_name,ship_name,pos):
	predef = defs.premade_ships[predef_name]
	if not ship_name:
		ship_name = predef["default_name"]
	if not pos: return
	new_ship = ship.new(predef["ship"],spawner["owner"])
	new_ship["pos"] = copy.deepcopy(pos)
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
	print(new_ship["name"],new_ship["pos"])
	return new_ship
def get_random_pos(system,tile_options,no_ships_radius,near):
	data = defs.system_data[system]
	valid_tiles = []
	for tile_name in tile_options:
		for tile in data["tiles_by_terrain"][tile_name]:
			tx = int(tile["x"])
			ty = int(tile["y"])
			if no_ships_radius == None or no_ships_in_radius(tile["system"],tx,ty,no_ships_radius):
				is_near = True
				if near:
					is_near = False
					for entry in near:
						x = entry["x"]
						y = entry["y"]
						r = entry["radius"]
						dist_x = max(x,tx)-min(x,tx)
						dist_y = max(y,ty)-min(y,ty)
						if max(dist_x,dist_y) <= r:
							is_near = True
				if is_near:
					valid_tiles.append(tile)
	if len(valid_tiles):
		pick = random.choice(valid_tiles)
		pos = {
			"x": int(pick["x"]),
			"y": int(pick["y"]),
			"rotation": 0,
			"system": pick["system"]
		}
		return pos
def no_ships_in_radius(system_name,x,y,no_ships_radius):
	otiles = defs.objmaps[system_name]["tiles"]
	otile = otiles.get(x,y)
	r = no_ships_radius
	x = int(x)
	y = int(y)
	for i in range(x-r,x+r+1):
		for j in range(y-r,y+r+1):
			otile = otiles.get(i,j)
			if "ships" in otile:
				return False
	return True

from . import defs,ship,map,stats