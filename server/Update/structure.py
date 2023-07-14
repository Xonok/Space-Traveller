from server import Item,defs

blah = {
	"workers_min": ["workers","min"],
	"workers_max": ["workers","max"],
	"industry_min": ["industry","min"],
	"industry_max": ["industry","max"],
	"wealth_min": ["wealth","min"],
	"wealth_max": ["wealth","max"],
	"prestige_min": ["prestige","min"],
	"prestige_max": ["prestige","max"],
	"science_min": ["science","min"],
	"science_max": ["science","max"],
	"biotech_min": ["biotech","min"],
	"biotech_max": ["biotech","max"]
}

def pop(entity):
	if "pop" in entity: return
	table = {}
	for name in ["workers","industry","wealth","prestige","science","biotech"]:
		table[name] = details()
	if entity["population"]:
		table["workers"]["current"] = entity["population"]["workers"]
	for item,amount in entity.get_gear().items():
		for stat,data in blah.items():
			val = Item.prop(item,stat)
			if val:
				table[data[0]][data[1]] += val
	for stat,data in blah.items():
		val = Item.ship_prop(entity["ship"],stat)
		if val:
			table[data[0]][data[1]] += val
	entity["pop"] = table
def details():
	return {
		"current": 0,
		"min": 0,
		"max": 0,
		"change": 0
	}
def update_pos(entity):
	predef = defs.premade_structures.get(entity["name"])
	if not predef: return
	pos_1 = entity.get("pos")
	pos_2 = predef.get("pos")
	if not pos_2: return
	pos_1["x"] = pos_2["x"]
	pos_1["y"] = pos_2["y"]
	pos_1["system"] = pos_2["system"]