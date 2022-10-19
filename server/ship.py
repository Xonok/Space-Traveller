from . import gear,defs
types = defs.ships
def slots(name,gtype):
	if gtype not in types[name]["slots"]:
		return 99999
	return types[name]["slots"][gtype]
def slots_left(name,gtype,pgear):
	equipped = gear.equipped(gtype,pgear)
	max = slots(name,gtype)
	return max-equipped