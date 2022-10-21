from . import gear,defs
def slots(name,gtype):
	if gtype not in defs.ships[name]["slots"]:
		return 99999
	return defs.ships[name]["slots"][gtype]
def slots_left(name,gtype,pgear):
	equipped = gear.equipped(gtype,pgear)
	max = slots(name,gtype)
	return max-equipped