from server import defs

def init():
	for name,data in defs.spawners.items():
		for name2 in data["ships"].keys():
			predef = defs.predefined_ships[name2]
			if "bounty" not in predef or predef["bounty"] == 0:
				print("Predef "+name2+" is in use by spawner "+name+", but the bounty is 0.")
