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
		"name": item["name"]+" Blueprint",
		"desc": item["desc"],
		"img": "img/blueprint.webp",
		"size": 0,
		"price": item["price"]
	}
	if "tech" in item:
		table["tech"] = item["tech"]
	recipe = "\n"
	recipe += "\tLabor: "+str(data["labor"])+"\n"
	recipe += "\tInputs\n"
	for item,amount in data["inputs"].items():
		if item in items:
			idata = items[item]
		elif item in ship_types:
			idata = ship_types[item]
		else:
			raise Exception("Unknown item in blueprint: "+item)
		recipe += "\t\t"+idata["name"]+": "+str(amount)+"\n"
	recipe += "\tOutputs\n"
	for item,amount in data["outputs"].items():
		if item in items:
			idata = items[item]
		elif item in ship_types:
			idata = ship_types[item]
		else:
			raise Exception("Unknown item in blueprint: "+item)
		recipe += "\t\t"+idata["name"]+": "+str(amount)+"\n"
	table["desc"] += recipe
	return table
prop_to_text = {
	"mount": "Mount",
	"hardpoint": "hardpoint",
	"type": "Type",
	"laser": "laser",
	"kinetic": "kinetic",
	"pd": "point defence",
	"missile":"missile",
	"damage": "Damage",
	"shots": "Shots",
	"shots_pd": "Point Defense",
	"targets": "Targets",
	"charge": "Rounds per attack",
	"tracking": "Tracking",
	"ammo":"Ammo",
	"duration":"Duration",
	"func": None,
	"input": "Input",
	"output": "Output",
	"cost": None,
	"armor_max": "Max armor",
	"armor_soak": "Protection",
	"armor_reg": "Regeneration",
	"shield_max": "Max shield",
	"shield_reg": "Regeneration",
	"shield_block": "Blocking",
	"manual": "Usable",
	"aura_space_bonus": "Extra space",
	"aura_speed_penalty": "Speed penalty",
	"aura_agility_penalty": "Agility penalty",
	"aura_speed_bonus": "Speed bonus",
	"space_max": "Extra space",
	"station_mining": "Allows a station to mine",
	"min_pop": "Minimum population",
	"max_pop": "Maximum population",
	"slots": "Slots",
	"space": "Max space",
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
	"module": "module",
	"drone": "drone",
	"habitation": "habitation",
	"none": "none",
	"tech": None,
	"weight": "weight",
	"tags": None,
	"hwr_charges": "hwr charges"
}
def add_props(name,item):
	item["prop_info"] = []
	info = item["prop_info"]
	props = item.get("props")
	if props:
		for key,value in props.items():			
			t = {}
			t["key"] = prop_to_text[key]
			if t["key"] == None: continue
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
def add_special(name,item,special,items):
	info = item["prop_info"]
	for key,value in special.items():
		t = {}
		t["key"] = prop_to_text[key]
		if t["key"] == None: continue
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
			t["value"] = prop_to_text[value]
def special2(items,*specials):
	for key,value in items.items():
		add_props(key,value)
	for special in specials:
		for key,value in special.items():
			if key in items:
				add_special(key,items[key],value,items)
			else:
				raise Exception("Unknown item: "+key)