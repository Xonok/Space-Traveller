import json
from server import defs

def run():
	obtainable = {}
	unobtainable = []
	def add(item,source_type,details):
		if item not in obtainable:
			obtainable[item] = {}
		if source_type not in obtainable[item]:
			obtainable[item][source_type] = []
		obtainable[item][source_type].append(details)
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
	#buy
	for name,data in defs.structures.items():
		if data["type"] != "planet": continue
		for item,data2 in data.get_prices().items():
			if "buy" in data2:
				add(item,"buy",name)
			if "buy" in data2:
				add(item,"sell",name)
	
	#look for unobtainable
	for item in defs.items.keys():
		if item not in obtainable:
			unobtainable.append(item)
	with open("obtainable.json","w") as f:
		json.dump(obtainable,f,indent="\t")
	with open("unobtainable.json","w") as f:
		json.dump(unobtainable,f,indent="\t")