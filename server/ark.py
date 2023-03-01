import copy
from . import defs,character,ship,map
def tick():
	check_default_ships()
	update_positions()
def check_default_ships():
	npc = character.data("Ark")
	predefined_ships = defs.npc_characters["Ark"]["ships_predefined"]
	temp = ship.gets("Ark")
	pships = {}
	for pship in temp.values():
		pships[pship["custom_name"]] = pship
	for predef_name in predefined_ships:
		data = defs.premade_ships[predef_name]
		ditems = {}
		dgear = {}
		if "inventory" in data:
			ditems = data["inventory"]["items"]
			dgear = data["inventory"]["gear"]
		ditems = data["inventory"]["items"]
		dgear = data["inventory"]["gear"]
		for name in data["names"]:
			if name in pships: continue
			new_ship = ship.new(data["type"],"Ark")
			new_ship["pos"] = copy.deepcopy(data["pos"])
			new_ship["loot"] = data["loot"]
			new_ship["predef"] = predef_name
			for item,amount in ditems.items():
				new_ship["inventory"]["items"].add(item,amount)
			for item,amount in ditems.items():
				new_ship["inventory"]["gear"].add(item,amount)
			map.add_ship2(new_ship)
			npc["ships"].append(new_ship["name"])
			new_ship.save()
	npc.save()
def update_positions():
	npc = character.data("Ark")
	pships = ship.gets("Ark")
	for name,pship in pships.items():
		predef = defs.premade_ships[pship["predef"]]
		if not map.pos_equal(pship["pos"],predef["pos"]):
			map.remove_ship(pship)
			pship["pos"] = copy.deepcopy(predef["pos"])
			stats = pship["stats"]
			stats["hull"]["current"] = stats["hull"]["max"]
			stats["armor"]["current"] = stats["shield"]["max"]
			stats["shield"]["current"] = stats["shield"]["max"]
			map.add_ship2(pship)
			pship.save()