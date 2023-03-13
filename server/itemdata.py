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
	"damage": "Damage",
	"shots": "Shots",
	"shots_pd": "Shots(point defense)",
	"targets": "Targets",
	"charge": "Rounds per attack",
	"func": None,
	"input": "Input",
	"output": "Output",
	"cost": None
}
def special(name,item,special,items):
	item["prop_info"] = []
	info = item["prop_info"]
	for key,value in special.items():
		t = {}
		t["key"] = prop_to_text[key]
		if t["key"] == None: continue
		info.append(t)
		if type(value) == int:
			t["value"] = value
		elif type(value) == dict:
			for k,v in value.items():
				t2 = {}
				t2["key"] = "\t"+items[k]["name"]
				if type(v) == int:
					t2["value"] = v
				else:
					t2["value"] = prop_to_text[v]
				info.append(t2)
			print(value)
		else:
			t["value"] = prop_to_text[value]
