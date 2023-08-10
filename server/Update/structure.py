from server import Item,defs

def update_pos(entity):
	predef = defs.premade_structures.get(entity["name"])
	if not predef: return
	pos_1 = entity.get("pos")
	pos_2 = predef.get("pos")
	if not pos_2: return
	pos_1["x"] = pos_2["x"]
	pos_1["y"] = pos_2["y"]
	pos_1["system"] = pos_2["system"]
def update_desc(entity):
	predef = defs.premade_structures.get(entity["name"])
	if not predef: return
	if "desc" not in predef: return
	desc = predef["desc"]
	if desc.startswith("%") and desc.endswith("%"):
		desc = desc[1:-1]
		if desc not in defs.lore: print("Missing lore entry: "+desc)
		desc = defs.lore[desc]
	entity["desc"] = desc
def assigned_industries(entity):
	if entity["name"] not in defs.assigned_industries: return
	if "industries" not in entity:
		entity["industries"] = []
	existing = {}
	for data in entity["industries"]:
		existing[data["name"]] = data
	entity["industries"] = []
	for name in defs.assigned_industries[entity["name"]]:
		if name in existing:
			entity["industries"].append(existing[name])
		else:
			itype = defs.industries2[name]
			entity["industries"].append({
				"name": name,
				"type": itype["type"],
				"workers": 0,
				"growth": 0,
				"migration": 0,
				"supply_ratio": 0.0
			})
