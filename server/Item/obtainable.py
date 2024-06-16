import json,collections
from server import defs

def run():
	obtainable = {}
	unobtainable = []
	dumpable = {}
	undumpable = []
	item_types = {}
	skill_items = {}
	def add(item,source_type,details):
		if item not in obtainable:
			obtainable[item] = {}
		if source_type not in obtainable[item]:
			obtainable[item][source_type] = []
		obtainable[item][source_type].append(details)
	def add_dumpable(item,source_type,details):
		if item not in dumpable:
			dumpable[item] = {}
		if source_type not in dumpable[item]:
			dumpable[item][source_type] = []
		dumpable[item][source_type].append(details)
	#gathering and extra
	for name,data in defs.gatherables.items():
		for item in data["output"].keys():
			add(item,"gathering",name)
		for item in data.get("extra",{}).keys():
			add(item,"gathering:extra",name)
	#factories
	for name,data in defs.machines.items():
		for item in data["output"].keys():
			add(item,"factory",name)
	#blueprints
	for name,data in defs.blueprints.items():
		for item in data["outputs"].keys():
			add(item,"blueprint",name)
	#loot
	#TODO: dealing with nested loot
	entity_loot = {}
	loot_entity = {}
	for name,data in defs.premade_ships.items():
		if "loot" in data:
			entity_loot[name] = data["loot"]
			if data["loot"] not in loot_entity:
				loot_entity[data["loot"]] = []
			loot_entity[data["loot"]].append(name)
	for name,data in defs.loot.items():
		for roll in data["rolls"]:
			if not "reroll" in roll:
				if name in loot_entity:
					add(roll["item"],"loot",name+"("+str(loot_entity[name])+")")
				else:
					add(roll["item"],"loot",name)
	#excavation
	#TBD
	#industry
	for name,data in defs.industries2.items():
		for item in data.get("output",{}).keys():
			add(item,"industry",name)
	#buy - commented out because it's too spammy
	#for name,data in defs.structures.items():
	#	if data["type"] != "planet": continue
	#	for item,data2 in data.get_prices().items():
	#		if "buy" in data2:
	#			add(item,"buy",name)
	#		if "buy" in data2:
	#			add(item,"sell",name)
	#planetary production(not industry)
	for name,data in defs.predefined_structures.items():
		for list_name in data["market"]["lists"]:
			price_list = defs.price_lists[list_name]
			for item in price_list["items"]:
				add_dumpable(item,"planet",name)
			if "generate_demand" not in price_list: continue
			for item in price_list["items"]:
				add(item,"planet",name)
	#look for unobtainable
	
	#process for better readability
	for name,data in obtainable.items():
		for key,data2 in data.items():
			if type(data2) == list:
				obtainable[name][key] = ", ".join(data2)
	
	for item,data in defs.items.items():
		if item not in obtainable:
			unobtainable.append(item)
		if item not in dumpable:
			undumpable.append(item)
		itype = data["type"]
		icat = defs.item_categories[itype]
		skill = icat.get("skill")
		tech = data.get("tech",0)
		if itype not in item_types:
			item_types[itype] = {}
		if tech not in item_types[itype]:
			item_types[itype][tech] = []
		item_types[itype][tech].append(item)
		if skill:
			if skill not in skill_items:
				skill_items[skill] = {}
			if tech not in skill_items[skill]:
				skill_items[skill][tech] = []
			skill_items[skill][tech].append(item)
	for itype,data in item_types.items():
		item_types[itype] = collections.OrderedDict(sorted(data.items()))
	for skill,data in skill_items.items():
		skill_items[skill] = collections.OrderedDict(sorted(data.items()))
	with open("obtainable.json","w") as f:
		json.dump(obtainable,f,indent="\t")
	with open("unobtainable.json","w") as f:
		json.dump(unobtainable,f,indent="\t")
	with open("dumpable.json","w") as f:
		json.dump(dumpable,f,indent="\t")
	with open("undumpable.json","w") as f:
		json.dump(undumpable,f,indent="\t")
	with open("item_types.json","w") as f:
		json.dump(item_types,f,indent="\t")
	with open("skill_items.json","w") as f:
		json.dump(skill_items,f,indent="\t")