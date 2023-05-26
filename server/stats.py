def make_scale(max,soak,resist,reg):
	return {
		"max": max,
		"current": max,
		"soak": soak,		#flat damage reduction
		"resist": resist,	#percent damage reduction
		"reg": reg
	}
def regenerate_armor(pship):
	regenerate(pship,"hull")
	regenerate(pship,"armor")
def regenerate(pship,stat_name):
	sgear = pship["inventory"]["gear"]
	stats = pship["stats"]
	total_reg = 0
	for item,amount in sgear.items():
		idata = defs.items[item]
		props = idata.get("props",{})
		reg = props.get(stat_name+"_reg")
		if reg:
			total_reg += reg*amount
	total_reg = min(total_reg,stats[stat_name]["max"]-stats[stat_name]["current"])
	stats[stat_name]["current"] += total_reg
	return total_reg
def update_ship(pship):
	prev = {}
	if "stats" in pship:
		prev = pship["stats"]
	shipdef = defs.ship_types[pship["type"]]
	default = {
		"hull": make_scale(shipdef["hull"],0,0,0),
		"armor": make_scale(0,0,0,0),
		"shield": make_scale(0,0,0,0)
	}
	pship["stats"] = default | prev
	stats = pship["stats"]
	prev_armor_max = stats["armor"]["max"]
	pship["stats"]["hull"]["max"] = shipdef["hull"]
	stats["armor"]["max"] = 0
	stats["armor"]["soak"] = 0	
	stats["armor"]["reg"] = 0
	stats["shield"]["max"] = 0
	stats["shield"]["reg"] = 0
	stats["speed"] = shipdef["speed"]
	stats["agility"] = shipdef["agility"]
	stats["agility"] = shipdef["agility"]
	stats["size"] = shipdef["size"]
	stats["weight"] = shipdef["size"]
	for item,amount in pship["inventory"]["gear"].items():
		idata = defs.items[item]
		props = idata.get("props",{})
		if "armor_max" in props:
			stats["armor"]["max"] += amount*props["armor_max"]
		if "armor_soak" in props:
			stats["armor"]["soak"] += amount*props["armor_soak"]
		if "armor_reg" in props:
			stats["armor"]["reg"] += amount*props["armor_reg"]
		if "shield_max" in props:
			stats["shield"]["max"] += amount*props["shield_max"]
		if "shield_reg" in props:
			stats["shield"]["reg"] += amount*props["shield_reg"]
		if "weight" in props:
			stats["weight"] += amount*props["weight"]
	stats["agility"] = int(stats["agility"] * stats["size"]/stats["weight"])
	if stats["armor"]["max"] > prev_armor_max:
		stats["armor"]["current"] += stats["armor"]["max"]-prev_armor_max
	if stats["armor"]["current"] > stats["armor"]["max"]:
		stats["armor"]["current"] = stats["armor"]["max"]
	stats["shield"]["current"] = stats["shield"]["max"]
	pship.save()
from . import defs