import random
from . import defs,map
def drop(target):
	if "loot" not in target: return
	loot_table = defs.loot[target["loot"]]
	pos = target["pos"]
	objmap = map.objmap(pos["system"])
	print(objmap)
	objtile = objmap.get(pos["x"],pos["y"])
	print(objtile)
	if "items" not in objtile:
		objtile["items"] = {}
	for data in loot_table["rolls"]:
		if random.randint(1,data["rarity"]) == 1:
			item = data["item"]
			if item not in objtile["items"]:
				objtile["items"][item] = 0
			objtile["items"][item] += random.randint(data["min"],data["max"])
	objmap.set(pos["x"],pos["y"],objtile)
	objmap.save()
