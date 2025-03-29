from server import defs
def init():
	for name,data in defs.spawners.items():
		if "pos" in data:
			x = str(data["pos"]["x"])
			y = str(data["pos"]["y"])
			sys_name = data["pos"]["system"]
			basetiles = defs.systems[sys_name]["tiles"]
			if x not in basetiles or y not in basetiles[x]:
				print("Invalid location in spawner: "+name,data["pos"])
		for name in data["ships"].keys():
			predef = defs.predefined_ships[name]
			if "spawner_count" not in predef:
				predef["spawner_count"] = 0
			predef["spawner_count"] += 1