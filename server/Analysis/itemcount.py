import json,os
from server import defs,io

def run():
	counts = {}
	def process(inv):
		for item,amount in inv.items():
			counts[item] += amount
	for name in defs.items.keys():
		counts[name] = 0
	for name in defs.ship_types.keys():
		counts[name] = 0
	for data in defs.ships.values():
		counts[data["type"]] += 1
	for data in defs.characters.values():
		process(data.get_items())
	for data in defs.ships.values():
		process(data.get_gear())
	for data in defs.structures.values():
		process(data.get_items())
		process(data.get_gear())
		counts[data["ship"]] += 1
	counts = dict(sorted(counts.items(),key=lambda e: e[1],reverse=True))
	path = os.path.join("output","item_counts.json")
	io.check_dir(path)
	with open(path,"w") as f:
		json.dump(counts,f,indent="\t")
run()