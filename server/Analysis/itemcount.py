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
	counts_noimg = {}
	for item,amount in counts.items():
		if item in defs.items:
			idata = defs.items[item]
		elif item in defs.ship_types:
			idata = defs.ship_types[item]
		else:
			raise Exception("Unknown item or ship: "+item)
		img_path = idata["img"]
		if not os.path.exists(img_path):
			counts_noimg[item] = amount
	path = os.path.join("output","item_counts.json")
	path2 = os.path.join("output","item_counts_noimg.json")
	io.check_dir(path)
	with open(path,"w") as f:
		json.dump(counts,f,indent="\t")
	with open(path2,"w") as f:
		json.dump(counts_noimg,f,indent="\t")
	
run()