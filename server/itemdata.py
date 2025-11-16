import copy

def blueprint(name,data):
	output = next(iter(data["outputs"]))
	if output in defs.items:
		item = defs.items[output]
		if "type" in item:
			item_type = item["type"]
		else:
			item_type = "other"
	elif output in defs.ship_types:
		item = defs.ship_types[output]
		item_type = "ship"
	else:
		raise Exception("Unknown blueprint result: "+output+" for blueprint "+name)
	table = {
		"type": "blueprint",
		"bp_category": item_type,
		"name": "Blueprint: "+item["name"],
		"desc": "Description: "+item["desc"],
		"img": "img/blueprint.webp",
		"size": 0,
		"price": item["price"]
	}
	if "tech" in item:
		table["tech"] = item["tech"]
	if "slots" in item:
		table["slots"] = item["slots"]
	recipe = "\n"
	recipe += "\tLabor: "+str(data["labor"])+"\n"
	recipe += "\tInputs\n"
	for item2,amount in data["inputs"].items():
		if item2 in defs.items:
			idata = defs.items[item2]
		elif item2 in defs.ship_types:
			idata = defs.ship_types[item2]
		else:
			raise Exception("Unknown item in blueprint: "+item2)
		recipe += "\t\t"+idata["name"]+": "+str(amount)+"\n"
	recipe += "\tOutputs\n"
	for item2,amount in data["outputs"].items():
		if item2 in defs.items:
			idata = defs.items[item2]
		elif item2 in defs.ship_types:
			idata = defs.ship_types[item2]
		else:
			raise Exception("Unknown item in blueprint: "+item2)
		recipe += "\t\t"+idata["name"]+": "+str(amount)+"\n"
	table["desc"] += recipe
	return table
def init():
	for name,data in defs.ship_types.items():
		tags = data.get("tags",{})
		if "hive" in tags:
			data["size_item"] = int(data["size"]*0.2)
		else:
			data["size_item"] = int(data["size"]*0.4)
	for bp_name,bp_data in defs.blueprints.items():
		idata = defs.items[bp_name]
		output_name = next(iter(bp_data["outputs"]))
		if output_name in defs.items:
			output_data = defs.items[output_name]
			if "type" in output_data:
				item_type = output_data["type"]
			else:
				item_type = "other"
		elif output_name in defs.ship_types:
			output_data = defs.ship_types[output_name]
			item_type = "ship"
		if len(output_data["prop_info"]):
			prop_text = "Stats\n"
			if output_name in defs.items:
				prop_text += "\tSize: "+str(output_data["size"])+"\n"
			for data in output_data["prop_info"]:
				key = data["key"]
				value = data.get("value")
				if value != None:
					prop_text += "\t"+key+": "+str(value)+"\n"
				else:
					prop_text += "\t"+key+"\n"
			idata["desc"] += prop_text
prop_to_text = {
	"mount": "Mount",
	"hardpoint": "hardpoint",
	"type": "Type",
	"laser": "laser",
	"kinetic": "kinetic",
	"pd": "point defence",
	"plasma": "plasma",
	"missile":"missile",
	"damage": "Damage",
	"damage_shield": "Damage to shield",
	"damage_armor": "Damage to armor",
	"damage_hull": "Damage to hull",
	"shots": "Shots",
	"shots_pd": "Point Defense",
	"targets": "Targets",
	"charge": "Rounds per attack",
	"preload": "Starts loaded",
	"tracking": "Tracking",
	"ammo": "Ammo",
	"duration": "Duration",
	"launch": "Launch",
	"func": None,
	"input": "Input",
	"output": "Output",
	"cost": None,
	"hull_reg": "Hull repair",
	"armor_max": "Max armor",
	"armor_soak": "Protection",
	"armor_reg": "Armor repair",
	"dampen": "Dampening",
	"block": "Block",
	"shield_max": "Max shield",
	"shield_reg": "Regeneration",
	"shield_block": "Blocking",
	"stealth": "Stealth",
	"deflect": "Deflect",
	"manual": "Usable",
	"aura_room_bonus": "Extra room",
	"aura_speed_penalty": "Speed penalty",
	"aura_agility_penalty": "Agility penalty",
	"aura_tracking_penalty": "Tracking penalty",
	"aura_speed_bonus": "Speed bonus",
	"room_max": "Extra room",
	"station_mining": "Allows a station to mine",
	"workers_max_construction": "Maximum construction workers",
	"robots_max_construction": "Maximum construction robots",
	"recycle_max": "Maximum recycling power",
	"recycle_reg": "Recycling power regeneration",
	"workers_max_research": "Maximum research workers",
	"robots_max_research": "Maximum research robots",
	"faction": "Faction",
	"slots": "Slots",
	"room": "Cargo space",
	"room_gear": "Equip space",
	"size": "External size",
	"hull": "Hull",
	"speed": "Speed",
	"agility": "Agility",
	"control": "Control",
	"price": None,
	"name": None,
	"img": None,
	"desc": None,
	"prop_info": None,
	"props": None,
	"gun": "gun",
	"shield": "shield",
	"armor": "armor",
	"hive_homeworld_return": "return device",
	"aura": "aura",
	"expander": "expander",
	"factory": "factory",
	"sensor": "sensor",
	"drone": "drone",
	"habitation": "habitation",
	"none": "none",
	"tech": None,
	"weight": "Weight",
	"tags": None,
	"hwr_charges": "hwr charges",
	"ship_predef": None,
	"turret": "turret",
	"module": "module",
	"mining": "mining",
	"farm": "farm",
	"consumable": "consumable",
	"True": "yes",
	"transport": "transport",
	"transport_capacity": "transport capacity",
	"transport_power": "transport power",
	"tile_limit": "allowed tiles",
	"transport_capacity_mod": "transport capacity modifier",
	"transport_power_mod": "transport power modifier",
	"skill_req": "skill requirements",
	"battle": "Battle points",
	"freight": "Freight points",
	"armor_bonus_factor": "Extra armor ratio",
	"shield_bonus_factor": "Extra shield ratio",
	"mining_power_energy": "Energy collection",
	"mining_power_nebula": "Gas collection",
	"mining_power_asteroids": "Asteroid mining",
	"mining_power_exotic": "Exotic Matter mining",
	"mining_power_phase": "Phase Vapor mining",
	"mining_bonus_asteroids": "Asteroid mining bonus",
	"mining_efficiency": "Mining efficiency"
}
def add_props(name,item):
	item["prop_info"] = []
	info = item["prop_info"]
	props = item.get("props")
	itype = Item.query.type(name)
	item_category = defs.item_categories[itype]
	item["prop_info"].append({
		"key": "Type",
		"value": item_category["name"]
	})
	if "tech" in item:
		item["prop_info"].append({
			"key": "Tech",
			"value": item["tech"]
		})
	if "grade" in item:
		item["prop_info"].append({
			"key": "Grade",
			"value": item["grade"]
		})
	if "tech" in item:
		itype = Item.query.type(name)
		item_category = defs.item_categories[itype]
		skill = item_category.get("skill")
		if skill:
			item["prop_info"].append({
				"key": "Skill",
				"value": defs.skills[skill]["name"]+"("+str(item["tech"])+")"
			})
	if "size" in item:
		item["prop_info"].append({
			"key": "Size",
			"value": item["size"]
		})
	if props:
		for key,value in props.items():
			if key not in prop_to_text:
				raise Exception("Unknown key '"+key+"' in "+name)
			t = {}
			t["key"] = prop_to_text[key]
			if t["key"] is None: continue
			t["value"] = value
			if type(value) == str:
				t["value"] = prop_to_text[value]
			info.append(t)
			if key in ["mining_bonus_energy","mining_bonus_nebula","mining_bonus_asteroids","mining_bonus_exotic","mining_bonus_phase"]:
				del t["value"]
				for k,v in value.items():
					t2 = {}
					t2["key"] = "\t"+defs.items[k]["name"]
					t2["value"] = v
				continue
			if type(value) == dict:
				del t["value"]
				for k,v in value.items():
					t2 = {}
					t2["key"] = "\t"+prop_to_text[k]
					t2["value"] = v
					info.append(t2)
def add_special(item,special,items):
	info = item["prop_info"]
	if "input" in special:
		item["input"] = copy.deepcopy(special["input"])
	if "output" in special:
		item["output"] = copy.deepcopy(special["output"])
	for key,value in special.items():
		t = {}
		t["key"] = prop_to_text[key]
		if t["key"] is None: continue
		info.append(t)
		if type(value) in [int,float]:
			t["value"] = value
		elif type(value) == dict:
			if key == "slots":
				for k,v in value.items():
					t2 = {}
					t2["key"] = "\t"+prop_to_text[k]
					if type(v) == int:
						t2["value"] = v
					else:
						t2["value"] = prop_to_text[v]
					info.append(t2)
			else:
				for k,v in value.items():
					t2 = {}
					t2["key"] = "\t"+items[k]["name"]
					if type(v) == int:
						t2["value"] = v
					else:
						t2["value"] = prop_to_text[v]
					info.append(t2)
		elif key == "faction":
			t["value"] = defs.factions[value]["name"]
		else:
			t["value"] = prop_to_text[str(value)]
def special2(items,*specials):
	for key,value in items.items():
		add_props(key,value)
	for special in specials:
		for key,value in special.items():
			if key in items:
				add_special(items[key],value,items)
			else:
				raise Exception("Unknown item: "+key)
from . import defs,Item