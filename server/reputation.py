import math
from server import defs,Skill,func

def check_structure(tstruct):
	if "props" not in tstruct:
		tstruct["props"] = {}
	if "reputation" not in tstruct["props"]:
		tstruct["props"]["reputation"] = {}
def add_rep(cdata,tstruct,item,amount):
	if tstruct["name"] not in defs.predefined_structures: return 0
	check_structure(tstruct)
	rep = tstruct["props"]["reputation"]
	name = cdata["name"]
	balance = tstruct["market"]["balance"]
	idata = defs.items.get(item)
	itype = "ship" if not idata else idata["type"]
	commodity = itype == "common" or itype == "produced" or itype == "rare"
	no_xp = False
	if item in balance["produced"] and item in balance["consumed"]:
		effect = 0
	elif item in balance["produced"]:
		effect = -1
	elif item in balance["consumed"]:
		effect = 1
	elif commodity:
		no_xp = True
		effect = -0.5
	else:
		return 0
	rep_amount = int(amount*effect)
	if rep_amount < 0:
		rep_amount = int(rep_amount*3)
	if name not in rep:
		rep[name] = 0
	rep[name] += rep_amount
	rep_level = max(int(math.log(max(rep[name]/50,1),2)),0)
	mult = 1 #TODO: should depend on location
	noob_factor = 1
	if cdata["level"] < 10:
		noob_factor += (9-cdata["level"])
	rep_factor = 1
	if rep[name] > 0:
		rep_factor = 1+math.log(max(rep[name]/100,1),2)/5
	elif rep[name] < 0:
		rep_factor = 1/(1+math.log(max(-rep[name]/100,1),2)/5)
	level_factor = 1/(cdata["level"]+1)
	xp = func.f2ir(abs(amount)*level_factor*mult*noob_factor*rep_factor)
	if rep_amount < 0 or no_xp:
		xp = 0
	tstruct.save()
	return xp
def tick(tstruct):
	if tstruct["name"] not in defs.predefined_structures: return
	check_structure(tstruct)
	rep = tstruct["props"]["reputation"]
	to_delete = []
	for name,amount in rep.items():
		if amount > 0:
			rep[name] = round(amount*0.995-1)
		else:
			rep[name] = round(amount*0.995+1)
		if rep[name] == 0:
			to_delete.append(name)
	for name in to_delete:
		del rep[name]
		