def blueprint(name,data,items,ship_types):
	output = next(iter(data["outputs"]))
	if output in items:
		item = items[output]
		if "type" in item:
			item_type = item["type"]
		else:
			item_type = "other"
	elif output in ship_types:
		item = ship_types[output]
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
		if item2 in items:
			idata = items[item2]
		elif item2 in ship_types:
			idata = ship_types[item2]
		else:
			raise Exception("Unknown item in blueprint: "+item2)
		recipe += "\t\t"+idata["name"]+": "+str(amount)+"\n"
	recipe += "\tOutputs\n"
	for item2,amount in data["outputs"].items():
		if item2 in items:
			idata = items[item2]
		elif item2 in ship_types:
			idata = ship_types[item2]
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
			for data in output_data["prop_info"]:
				key = data["key"]
				value = data.get("value")
				if value:
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
	"shots": "Shots",
	"shots_pd": "Point Defense",
	"targets": "Targets",
	"charge": "Rounds per attack",
	"preload": "Starts loaded",
	"tracking": "Tracking",
	"ammo":"Ammo",
	"duration":"Duration",
	"func": None,
	"input": "Input",
	"output": "Output",
	"cost": None,
	"hull_reg": "Hull repair",
	"armor_max": "Max armor",
	"armor_soak": "Protection",
	"armor_reg": "Armor repair",
	"shield_max": "Max shield",
	"shield_reg": "Regeneration",
	"shield_block": "Blocking",
	"stealth": "Stealth",
	"manual": "Usable",
	"aura_room_bonus": "Extra room",
	"aura_speed_penalty": "Speed penalty",
	"aura_agility_penalty": "Agility penalty",
	"aura_tracking_penalty": "Tracking penalty",
	"aura_speed_bonus": "Speed bonus",
	"room_max": "Extra room",
	"station_mining": "Allows a station to mine",
	"workers_max_construction": "Maximum construction workers",
	"slots": "Slots",
	"room": "Max room",
	"size": "Size",
	"hull": "Hull",
	"speed": "Speed",
	"agility": "Agility",
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
	"True": "yes"
}
def add_props(name,item):
	item["prop_info"] = []
	info = item["prop_info"]
	props = item.get("props")
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
			if type(value) == dict:
				del t["value"]
				for k,v in value.items():
					t2 = {}
					t2["key"] = "\t"+prop_to_text[k]
					t2["value"] = v
					info.append(t2)
def add_special(item,special,items):
	info = item["prop_info"]
	for key,value in special.items():
		t = {}
		t["key"] = prop_to_text[key]
		if t["key"] is None: continue
		info.append(t)
		if type(value) == int:
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
from . import defs