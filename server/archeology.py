from . import defs,ship,error,loot
def excavate(data,pdata):
	pship = ship.get(pdata.ship())
	pos = pship["pos"]
	if pos["system"] not in defs.excavations:
		raise error.User("There is nothing to excavate in this entire system.")
	grid = defs.excavations[pos["system"]]
	tile = grid.get(pos["x"],pos["y"])
	if "loot" not in tile:
		raise error.User("Nothing to excavate in this particular location.")
	loot.drop2(tile["loot"],pos)