from . import defs
def display():
	itypes = {}
	for item,data in defs.items.items():
		itype = data.get("type")
		if itype not in itypes:
			itypes[itype] = 0
		itypes[itype] += 1
	itypes = dict(sorted(itypes.items(), key=lambda item: item[1],reverse=True))
	print("Items:",len(defs.items))
	for itype,amount in itypes.items():
		print("\t"+itype,amount)
	#print("\tWeapons:",len(defs.weapons))
	#print("\tMachines:",len(defs.machines))
	#print("\tBlueprints:",len(defs.blueprints))
	print("Ship types:",len(defs.ship_types))
	print("Constellations:",len(defs.constellations),list(defs.constellations.keys()))
	print("Stars:",len(defs.systems),list(defs.systems.keys()))
	print("Players:",len(defs.users),list(defs.users.keys()))
	print("Characters:",len(defs.characters))
	player_characters = []
	for name in defs.characters.keys():
		if name not in defs.npc_characters:
			player_characters.append(name)
	print("\tPlayers:",len(player_characters),player_characters)
	print("\tNPCs:",len(defs.npc_characters),list(defs.npc_characters.keys()))
	print("Ships:",len(defs.ships))
	npc_ships = 0
	character_ships = 0
	for character,names in defs.character_ships.items():
		if character in defs.npc_characters:
			npc_ships += len(names)
		else:
			character_ships += len(names)
	print("\tNPC:",npc_ships)
	print("\tPlayer:",character_ships)