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
	for name in predefined_ships:
		if name not in pships:
			shipdef = defs.premade_ships[name]
			new_ship = ship.new(shipdef["type"],"Ark")
			for key,value in shipdef.items():
				new_ship[key] = value
			map.add_ship2(new_ship)
			npc["ships"].append(new_ship["name"])
			new_ship.save()
	npc.save()
def update_positions():
	npc = character.data("Ark")
	pships = ship.gets("Ark")
	for name,pship in pships.items():
		predef = defs.premade_ships[pship["custom_name"]]
		if not map.pos_equal(pship["pos"],predef["pos"]):
			map.remove_ship(pship)
			pship["pos"] = copy.deepcopy(predef["pos"])
			map.add_ship2(pship)
			pship.save()