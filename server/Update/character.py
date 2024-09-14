from server import defs,ship,map,types

def update(cdata):
	if "level" not in cdata:
		cdata["level"] = 0
	if "xp" not in cdata:
		cdata["xp"] = 0
	if "skills" not in cdata:
		cdata["skills"] = {}
	if cdata["name"] in defs.npc_characters: return
	if "home" not in cdata:
		cdata["home"] = "Megrez Prime"
def inventory_revamp():
	def add(table,item,amount):
		if item not in table:
			table[item] = 0
		table[item] += amount
	for name,cdata in defs.characters.items():
		if "items" not in cdata:
			cdata["items"] = types.make({},"items")
			types.instances = []
			cdata["items"].parent = cdata
			cdata["stats"] = {
				"room": {
					"current": 0,
					"max": 0
				}
			}
	for pship in defs.ships.values():
		if "inventory" not in pship: continue
		cdata = defs.characters[pship["owner"]]
		for item,amount in pship["inventory"]["items"].items():
			add(cdata["items"],item,amount)
		pship["gear"] = pship["inventory"]["gear"]
		del pship["inventory"]
		pship["stats"]["room"] = {
			"current": 0,
			"max": 0
		}
	for tstruct in defs.structures.values():
		if "inventory" not in tstruct: continue
		tstruct["items"] = tstruct["inventory"]["items"]
		tstruct["gear"] = tstruct["inventory"]["gear"]
		del tstruct["inventory"]
		tstruct["stats"]
		tstruct["stats"]["room"] = {
			"current": 0,
			"max": 0
		}
	for name,cdata in defs.characters.items():
		if name in defs.npc_characters: continue
		ship0 = ship.get(cdata["ships"][0])
		pos = ship0["pos"]
		for sname in defs.character_ships[name].values():
			pship = ship.get(sname)
			map.remove_ship(pship)
			map.add_ship(pship,pos["system"],pos["x"],pos["y"])
			if sname not in cdata["ships"]:
				cdata["ships"].append(sname)
		cdata.get_room()