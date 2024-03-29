from . import defs,ship,error,loot
def excavate(data,cdata):
	pship = ship.get(cdata.ship())
	pos = pship["pos"]
	if pos["system"] not in defs.excavations:
		raise error.User("There is nothing to excavate in this entire system.")
	grid = defs.excavations[pos["system"]]
	tile = grid.get(pos["x"],pos["y"])
	if "loot" not in tile:
		raise error.User("Nothing to excavate in this particular location.")
	if "level" in tile:
		can_excavate = False
		for item in items_or:
			idata = defs.items[item]
			props = idata.get("props",{})
			level = props.get("archeology_level",0)
			if level >= tile["level"]:
				can_excavate = True
				break
		if not can_excavate:
			raise error.User("Can't excavate here. Need a better scanner.")
	loot.drop2(tile["loot"],pship,True)
def investigate(self,data,cdata):
	pship = ship.get(cdata.ship())
	pos = pship["pos"]
	if pos["system"] not in defs.excavations:
		raise error.User("There are no signs of precursor activity in this system.")
	grid = defs.excavations[pos["system"]]
	tile = grid.get(pos["x"],pos["y"])
	if "info" not in tile:
		raise error.User("This location doesn't seem to have any archeological significance.")
	else:
		self.add_message(tile["info"])
def can_excavate(data,cdata):
	pship = ship.get(cdata.ship())
	pos = pship["pos"]
	if pos["system"] in defs.excavations:
		grid = defs.excavations[pos["system"]]
		tile = grid.get(pos["x"],pos["y"])
		if "loot" in tile:
			return True
def can_investigate(data,cdata):
	pship = ship.get(cdata.ship())
	pos = pship["pos"]
	if pos["system"] in defs.excavations:
		grid = defs.excavations[pos["system"]]
		tile = grid.get(pos["x"],pos["y"])
		if "info" in tile:
			return True